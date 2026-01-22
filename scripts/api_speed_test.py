import requests
import time
import statistics

# Test different scenarios
scenarios = [
    {"name": "Small (5 centers, 10 blocks)", "k": 5, "num_blocks": 10, "radius": 2.0},
    {"name": "Medium (10 centers, 50 blocks)", "k": 10, "num_blocks": 50, "radius": 2.0},
    {"name": "Large (15 centers, 100 blocks)", "k": 15, "num_blocks": 100, "radius": 3.0},
]

API_URL = "http://localhost:8000"  # Backend API server

print("Testing API response times...\n")

for scenario in scenarios:
    times = []
    
    # Run 5 times to get average
    for i in range(5):
        # You'll need to adjust this payload based on your actual API
        payload = {
            "affected_geoids": [f"29510{str(i).zfill(6)}" for i in range(scenario["num_blocks"])],
            "k": scenario["k"],
            "radius_miles": scenario["radius"]
        }
        
        start = time.time()
        try:
            response = requests.post(f"{API_URL}/api/optimize", json=payload, timeout=10)
            elapsed = time.time() - start
            
            if response.status_code == 200:
                times.append(elapsed)
            else:
                print(f"  Error: {response.status_code}")
        except Exception as e:
            print(f"  Error: {e}")
    
    if times:
        avg_time = statistics.mean(times)
        print(f"{scenario['name']}: {avg_time:.3f}s average ({min(times):.3f}s - {max(times):.3f}s)")
    else:
        print(f"{scenario['name']}: Failed to get timing")
    print()
