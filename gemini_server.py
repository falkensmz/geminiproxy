#!/usr/bin/env python3
"""
Gemini REST API Server
Provides HTTP endpoints for the Gemini CLI wrapper
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json
import threading
import uuid
from datetime import datetime
from gemini_api import GeminiAPI
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini API
gemini = GeminiAPI(auto_approve=True, checkpointing=True)

# Store for async job results
job_results = {}
job_lock = threading.Lock()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "usage": gemini.get_usage()
    })

@app.route('/usage', methods=['GET'])
def usage():
    """Get current usage statistics"""
    stats = gemini.get_usage()
    return jsonify(stats)

@app.route('/prompt', methods=['POST'])
def prompt():
    """Send a prompt to Gemini"""
    try:
        data = request.json
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing 'prompt' in request body"}), 400
        
        prompt_text = data['prompt']
        extra_flags = data.get('extra_flags', [])
        use_cache = data.get('use_cache', True)
        
        result = gemini.prompt(prompt_text, extra_flags=extra_flags, use_cache=use_cache)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing prompt: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/prompt/async', methods=['POST'])
def prompt_async():
    """Queue a prompt for async processing"""
    try:
        data = request.json
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing 'prompt' in request body"}), 400
        
        job_id = str(uuid.uuid4())
        
        def callback(result):
            with job_lock:
                job_results[job_id] = {
                    "status": "completed",
                    "result": result,
                    "completed_at": datetime.now().isoformat()
                }
        
        # Initialize job status
        with job_lock:
            job_results[job_id] = {
                "status": "processing",
                "started_at": datetime.now().isoformat()
            }
        
        gemini.prompt_async(
            data['prompt'],
            callback=callback,
            extra_flags=data.get('extra_flags', [])
        )
        
        return jsonify({
            "job_id": job_id,
            "status": "queued",
            "check_url": f"/job/{job_id}"
        })
    
    except Exception as e:
        logger.error(f"Error queuing prompt: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/job/<job_id>', methods=['GET'])
def get_job(job_id):
    """Check status of an async job"""
    with job_lock:
        if job_id not in job_results:
            return jsonify({"error": "Job not found"}), 404
        
        return jsonify(job_results[job_id])

@app.route('/batch', methods=['POST'])
def batch():
    """Process multiple prompts"""
    try:
        data = request.json
        if not data or 'prompts' not in data:
            return jsonify({"error": "Missing 'prompts' in request body"}), 400
        
        prompts = data['prompts']
        if not isinstance(prompts, list):
            return jsonify({"error": "'prompts' must be a list"}), 400
        
        # Process in background
        job_id = str(uuid.uuid4())
        
        def process_batch():
            results = gemini.batch_prompts(prompts)
            with job_lock:
                job_results[job_id] = {
                    "status": "completed",
                    "results": results,
                    "completed_at": datetime.now().isoformat()
                }
        
        # Initialize job status
        with job_lock:
            job_results[job_id] = {
                "status": "processing",
                "total_prompts": len(prompts),
                "started_at": datetime.now().isoformat()
            }
        
        thread = threading.Thread(target=process_batch)
        thread.start()
        
        return jsonify({
            "job_id": job_id,
            "status": "processing",
            "total_prompts": len(prompts),
            "check_url": f"/job/{job_id}"
        })
    
    except Exception as e:
        logger.error(f"Error processing batch: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/stream', methods=['POST'])
def stream():
    """Stream responses for a prompt (SSE)"""
    try:
        data = request.json
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing 'prompt' in request body"}), 400
        
        def generate():
            # Send initial status
            yield f"data: {json.dumps({'status': 'processing'})}\n\n"
            
            # Process prompt
            result = gemini.prompt(data['prompt'], extra_flags=data.get('extra_flags', []))
            
            # Send result
            yield f"data: {json.dumps(result)}\n\n"
            
            # Send completion
            yield f"data: {json.dumps({'status': 'completed'})}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
    
    except Exception as e:
        logger.error(f"Error in stream: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/jobs', methods=['GET'])
def list_jobs():
    """List all jobs"""
    with job_lock:
        jobs = []
        for job_id, job_data in job_results.items():
            jobs.append({
                "job_id": job_id,
                "status": job_data.get("status"),
                "started_at": job_data.get("started_at"),
                "completed_at": job_data.get("completed_at")
            })
        return jsonify({"jobs": jobs, "total": len(jobs)})

@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear the response cache"""
    gemini.response_cache.clear()
    return jsonify({"message": "Cache cleared", "status": "success"})

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Gemini REST API Server")
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    print(f"Starting Gemini API Server on {args.host}:{args.port}")
    print(f"API Documentation: http://{args.host}:{args.port}/")
    print("\nEndpoints:")
    print("  GET  /health         - Health check and usage stats")
    print("  GET  /usage          - Current usage statistics")
    print("  POST /prompt         - Send a prompt (sync)")
    print("  POST /prompt/async   - Queue a prompt (async)")
    print("  GET  /job/<id>       - Check job status")
    print("  POST /batch          - Process multiple prompts")
    print("  POST /stream         - Stream responses (SSE)")
    print("  GET  /jobs           - List all jobs")
    print("  POST /cache/clear    - Clear response cache")
    
    app.run(host=args.host, port=args.port, debug=args.debug)