#!/usr/bin/env python3
"""
Example usage scripts for the Gemini API wrapper
"""

import time
import json
import requests
from gemini_api import GeminiAPI

def example_basic_usage():
    """Basic API usage example"""
    print("=== Basic Usage Example ===\n")
    
    api = GeminiAPI()
    
    # Simple prompt
    result = api.prompt("Write a haiku about Python programming")
    
    if result["success"]:
        print("Response:")
        print(result["output"])
    else:
        print(f"Error: {result['error']}")
    
    # Check usage
    print("\nCurrent usage:")
    usage = api.get_usage()
    print(f"  Requests this hour: {usage['requests_last_hour']}/{usage['max_per_hour']}")
    print(f"  Remaining: {usage['remaining_this_hour']}")

def example_batch_processing():
    """Batch processing example"""
    print("=== Batch Processing Example ===\n")
    
    api = GeminiAPI()
    
    prompts = [
        "Explain quantum computing in one sentence",
        "What is the capital of France?",
        "Write a Python function to reverse a string",
        "List 3 benefits of exercise"
    ]
    
    print(f"Processing {len(prompts)} prompts...\n")
    results = api.batch_prompts(prompts)
    
    for i, (prompt, result) in enumerate(zip(prompts, results), 1):
        print(f"Prompt {i}: {prompt[:50]}...")
        if result["success"]:
            print(f"Response: {result['output'][:200]}...")
        else:
            print(f"Error: {result['error']}")
        print()

def example_async_processing():
    """Async processing with callbacks"""
    print("=== Async Processing Example ===\n")
    
    api = GeminiAPI()
    
    results = []
    
    def callback(result):
        results.append(result)
        print(f"Received response {len(results)}")
    
    # Queue multiple async requests
    prompts = [
        "Count from 1 to 5",
        "List the primary colors",
        "What is 2+2?"
    ]
    
    for prompt in prompts:
        response = api.prompt_async(prompt, callback=callback)
        print(f"Queued: {prompt} (queue size: {response['queue_size']})")
    
    # Wait for all to complete
    print("\nWaiting for responses...")
    while len(results) < len(prompts):
        time.sleep(1)
    
    print("\nAll responses received!")
    for i, result in enumerate(results, 1):
        if result["success"]:
            print(f"Result {i}: {result['output'][:100]}...")

def example_rest_api():
    """REST API usage example"""
    print("=== REST API Example ===\n")
    print("Note: Make sure the server is running with: python gemini_server.py\n")
    
    base_url = "http://127.0.0.1:5000"
    
    try:
        # Check health
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"Server Status: {health['status']}")
            print(f"Usage: {health['usage']['requests_last_hour']}/{health['usage']['max_per_hour']}")
        
        # Send a prompt
        prompt_data = {
            "prompt": "What is machine learning?",
            "use_cache": True
        }
        
        print("\nSending prompt via REST API...")
        response = requests.post(f"{base_url}/prompt", json=prompt_data)
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                print(f"Response: {result['output'][:200]}...")
            else:
                print(f"Error: {result['error']}")
        
        # Async prompt
        async_data = {
            "prompt": "Write a short poem about APIs"
        }
        
        print("\nSending async prompt...")
        response = requests.post(f"{base_url}/prompt/async", json=async_data)
        
        if response.status_code == 200:
            job_info = response.json()
            job_id = job_info["job_id"]
            print(f"Job ID: {job_id}")
            
            # Poll for result
            while True:
                time.sleep(2)
                response = requests.get(f"{base_url}/job/{job_id}")
                job_status = response.json()
                
                if job_status["status"] == "completed":
                    print("Job completed!")
                    if job_status["result"]["success"]:
                        print(f"Result: {job_status['result']['output'][:200]}...")
                    break
                else:
                    print(f"Job status: {job_status['status']}")
    
    except requests.exceptions.ConnectionError:
        print("Could not connect to server. Make sure it's running with:")
        print("  python gemini_server.py")

def example_rate_limit_handling():
    """Example of handling rate limits gracefully"""
    print("=== Rate Limit Handling Example ===\n")
    
    # Create API with very low limit for testing
    api = GeminiAPI(rate_limit_per_hour=5)
    
    prompts = [f"Test prompt {i}" for i in range(10)]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"Attempt {i}/10: ", end="")
        result = api.prompt(prompt)
        
        if result["success"]:
            print("Success!")
        elif "wait_time" in result:
            wait = result["wait_time"]
            print(f"Rate limited. Waiting {wait} seconds...")
            time.sleep(wait)
            # Retry after waiting
            result = api.prompt(prompt)
            if result["success"]:
                print("  Retry successful!")
        else:
            print(f"Error: {result['error']}")
        
        # Show current usage
        if "usage" in result:
            usage = result["usage"]
            print(f"  Usage: {usage['requests_last_hour']}/{usage['max_per_hour']}")

def example_with_caching():
    """Example showing caching behavior"""
    print("=== Caching Example ===\n")
    
    api = GeminiAPI()
    prompt = "What is the speed of light?"
    
    # First request
    print("First request (not cached):")
    start = time.time()
    result1 = api.prompt(prompt)
    time1 = time.time() - start
    print(f"  Time: {time1:.2f}s")
    print(f"  From cache: {result1.get('from_cache', False)}")
    
    # Second request (should be cached)
    print("\nSecond request (cached):")
    start = time.time()
    result2 = api.prompt(prompt)
    time2 = time.time() - start
    print(f"  Time: {time2:.2f}s")
    print(f"  From cache: {result2.get('from_cache', False)}")
    
    # Request without cache
    print("\nThird request (cache disabled):")
    start = time.time()
    result3 = api.prompt(prompt, use_cache=False)
    time3 = time.time() - start
    print(f"  Time: {time3:.2f}s")
    print(f"  From cache: {result3.get('from_cache', False)}")

if __name__ == "__main__":
    import sys
    
    examples = {
        "basic": example_basic_usage,
        "batch": example_batch_processing,
        "async": example_async_processing,
        "rest": example_rest_api,
        "rate": example_rate_limit_handling,
        "cache": example_with_caching
    }
    
    if len(sys.argv) > 1 and sys.argv[1] in examples:
        examples[sys.argv[1]]()
    else:
        print("Gemini API Examples")
        print("===================")
        print("\nUsage: python examples.py [example_name]")
        print("\nAvailable examples:")
        print("  basic  - Basic API usage")
        print("  batch  - Batch processing multiple prompts")
        print("  async  - Async processing with callbacks")
        print("  rest   - REST API server usage")
        print("  rate   - Rate limit handling")
        print("  cache  - Response caching")
        print("\nRunning all examples...\n")
        
        for name, func in examples.items():
            if name != "rest":  # Skip REST example if server not running
                func()
                print("\n" + "="*50 + "\n")
                time.sleep(2)