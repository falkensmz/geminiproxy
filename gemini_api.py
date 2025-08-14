#!/usr/bin/env python3
"""
Gemini CLI API Wrapper
Handles rate limiting (1000 requests/hour) and provides a clean interface
"""

import subprocess
import json
import time
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pathlib import Path
import threading
import queue
import hashlib

class GeminiRateLimiter:
    def __init__(self, max_requests_per_hour=950):  # Conservative limit
        self.max_requests = max_requests_per_hour
        self.db_path = Path.home() / ".gemini_rate_limit.db"
        self.init_db()
        self.lock = threading.Lock()
    
    def init_db(self):
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                prompt_hash TEXT,
                response_length INTEGER
            )
        ''')
        conn.commit()
        conn.close()
    
    def can_make_request(self) -> tuple[bool, Optional[int]]:
        with self.lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Clean old requests (older than 1 hour)
            cursor.execute('''
                DELETE FROM requests 
                WHERE timestamp < datetime('now', '-1 hour')
            ''')
            
            # Count recent requests
            cursor.execute('''
                SELECT COUNT(*) FROM requests 
                WHERE timestamp > datetime('now', '-1 hour')
            ''')
            count = cursor.fetchone()[0]
            conn.close()
            
            if count < self.max_requests:
                return True, None
            else:
                # Calculate wait time until oldest request expires
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT MIN(timestamp) FROM requests 
                    WHERE timestamp > datetime('now', '-1 hour')
                ''')
                oldest = cursor.fetchone()[0]
                conn.close()
                
                if oldest:
                    oldest_time = datetime.fromisoformat(oldest)
                    wait_until = oldest_time + timedelta(hours=1)
                    wait_seconds = (wait_until - datetime.now()).total_seconds()
                    return False, max(1, int(wait_seconds))
                return False, 60
    
    def record_request(self, prompt: str, response_length: int = 0):
        with self.lock:
            prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO requests (prompt_hash, response_length) 
                VALUES (?, ?)
            ''', (prompt_hash, response_length))
            conn.commit()
            conn.close()
    
    def get_usage_stats(self) -> Dict:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Requests in last hour
        cursor.execute('''
            SELECT COUNT(*) FROM requests 
            WHERE timestamp > datetime('now', '-1 hour')
        ''')
        hour_count = cursor.fetchone()[0]
        
        # Requests today
        cursor.execute('''
            SELECT COUNT(*) FROM requests 
            WHERE timestamp > datetime('now', 'start of day')
        ''')
        today_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "requests_last_hour": hour_count,
            "requests_today": today_count,
            "remaining_this_hour": self.max_requests - hour_count,
            "max_per_hour": self.max_requests
        }


class GeminiAPI:
    def __init__(self, 
                 auto_approve=True, 
                 checkpointing=True,
                 max_retries=3,
                 rate_limit_per_hour=950):
        self.auto_approve = auto_approve
        self.checkpointing = checkpointing
        self.rate_limiter = GeminiRateLimiter(rate_limit_per_hour)
        self.max_retries = max_retries
        self.request_queue = queue.Queue()
        self.response_cache = {}
        
        # Start background worker thread
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
    
    def _execute_gemini_command(self, prompt: str, extra_flags: List[str] = None) -> Dict:
        """Execute the gemini CLI command"""
        cmd = ["gemini"]
        
        if self.auto_approve:
            cmd.append("--yolo")
        if self.checkpointing:
            cmd.append("--checkpointing")
        
        if extra_flags:
            cmd.extend(extra_flags)
        
        cmd.extend(["-p", prompt])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
                "command": " ".join(cmd)
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": None,
                "error": "Command timed out after 5 minutes",
                "command": " ".join(cmd)
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": str(e),
                "command": " ".join(cmd)
            }
    
    def prompt(self, text: str, extra_flags: List[str] = None, use_cache: bool = True) -> Dict:
        """Send a prompt to Gemini with rate limiting and retry logic"""
        
        # Check cache first
        cache_key = hashlib.md5(f"{text}{extra_flags}".encode()).hexdigest()
        if use_cache and cache_key in self.response_cache:
            cached = self.response_cache[cache_key]
            cached["from_cache"] = True
            return cached
        
        # Check rate limit
        can_proceed, wait_time = self.rate_limiter.can_make_request()
        
        if not can_proceed:
            return {
                "success": False,
                "error": f"Rate limit reached. Please wait {wait_time} seconds.",
                "wait_time": wait_time,
                "usage": self.rate_limiter.get_usage_stats()
            }
        
        # Attempt with retries
        last_error = None
        for attempt in range(self.max_retries):
            if attempt > 0:
                time.sleep(2 ** attempt)  # Exponential backoff
            
            result = self._execute_gemini_command(text, extra_flags)
            
            if result["success"]:
                # Record successful request
                self.rate_limiter.record_request(text, len(result.get("output", "")))
                
                # Cache result
                if use_cache:
                    self.response_cache[cache_key] = result
                
                result["usage"] = self.rate_limiter.get_usage_stats()
                result["attempt"] = attempt + 1
                return result
            
            last_error = result["error"]
        
        # All retries failed
        return {
            "success": False,
            "error": f"Failed after {self.max_retries} attempts. Last error: {last_error}",
            "usage": self.rate_limiter.get_usage_stats()
        }
    
    def prompt_async(self, text: str, callback=None, extra_flags: List[str] = None):
        """Queue a prompt for async processing"""
        request = {
            "prompt": text,
            "extra_flags": extra_flags,
            "callback": callback,
            "timestamp": datetime.now()
        }
        self.request_queue.put(request)
        return {"queued": True, "queue_size": self.request_queue.qsize()}
    
    def _process_queue(self):
        """Background worker to process queued requests"""
        while True:
            try:
                request = self.request_queue.get(timeout=1)
                result = self.prompt(request["prompt"], request.get("extra_flags"))
                
                if request.get("callback"):
                    request["callback"](result)
                
                self.request_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Queue processing error: {e}")
    
    def get_usage(self) -> Dict:
        """Get current usage statistics"""
        return self.rate_limiter.get_usage_stats()
    
    def batch_prompts(self, prompts: List[str], parallel: bool = False) -> List[Dict]:
        """Process multiple prompts, respecting rate limits"""
        results = []
        
        for i, prompt in enumerate(prompts):
            print(f"Processing prompt {i+1}/{len(prompts)}...")
            
            # Check if we need to wait
            can_proceed, wait_time = self.rate_limiter.can_make_request()
            if not can_proceed:
                print(f"Rate limit reached. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
            
            result = self.prompt(prompt)
            results.append(result)
            
            # Small delay between requests
            if i < len(prompts) - 1:
                time.sleep(1)
        
        return results


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Gemini CLI API Wrapper")
    parser.add_argument("prompt", nargs="?", help="The prompt to send to Gemini")
    parser.add_argument("--no-yolo", action="store_true", help="Disable auto-approval")
    parser.add_argument("--no-checkpoint", action="store_true", help="Disable checkpointing")
    parser.add_argument("--stats", action="store_true", help="Show usage statistics")
    parser.add_argument("--batch", type=str, help="File with prompts (one per line)")
    parser.add_argument("--output", type=str, help="Output file for batch results")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    api = GeminiAPI(
        auto_approve=not args.no_yolo,
        checkpointing=not args.no_checkpoint
    )
    
    if args.stats:
        stats = api.get_usage()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print(f"Requests in last hour: {stats['requests_last_hour']}/{stats['max_per_hour']}")
            print(f"Remaining this hour: {stats['remaining_this_hour']}")
            print(f"Requests today: {stats['requests_today']}")
    
    elif args.batch:
        with open(args.batch, 'r') as f:
            prompts = [line.strip() for line in f if line.strip()]
        
        results = api.batch_prompts(prompts)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {args.output}")
        else:
            for i, result in enumerate(results):
                print(f"\n--- Result {i+1} ---")
                if result["success"]:
                    print(result["output"])
                else:
                    print(f"Error: {result['error']}")
    
    elif args.prompt:
        result = api.prompt(args.prompt)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result["success"]:
                print(result["output"])
            else:
                print(f"Error: {result['error']}")
                if "usage" in result:
                    print(f"\nUsage: {result['usage']['requests_last_hour']}/{result['usage']['max_per_hour']} requests this hour")
    
    else:
        parser.print_help()