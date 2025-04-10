import json
import os

import requests

# List of services
SERVICES = [
    "admin",
    "appointments",
    "charting",
    "communication",
    "medication",
    "notifications",
    "patients",
    "payments",
    "reports",
    "tasks",
    "therapies",
    "tickets"
]

# Base URL pattern (Replace `<service>` with actual service name)
BASE_URL = "https://uu3yiro3wl.execute-api.us-east-2.amazonaws.com/{}/docs-json"

# Output JSON file
OUTPUT_FILE = "services.json"


def fetch_swagger_json(url):
    """Fetch Swagger JSON from the given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Swagger JSON from {url}: {e}")
        return None


def extract_endpoints(swagger_data):
    """Extract endpoints and count them from Swagger JSON."""
    if not swagger_data or "paths" not in swagger_data:
        return {"totalEndpoints": 0, "endpoints": []}

    endpoints = []
    for path, methods in swagger_data["paths"].items():
        for method in methods:
            endpoints.append({"method": method.upper(), "path": path})

    return {"totalEndpoints": len(endpoints), "endpoints": endpoints}


def save_to_json(service_name, endpoint_data):
    """Append new service data to services.json and update totalAppEndpoints."""
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {"totalAppEndpoints": 0}
    else:
        data = {"totalAppEndpoints": 0}

    # Update service-specific data
    data[service_name] = endpoint_data

    # Recalculate total number of endpoints
    total_endpoints = sum(service["totalEndpoints"] for service in data.values() if isinstance(service, dict))
    data["totalAppEndpoints"] = total_endpoints

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Service '{service_name}' updated with {endpoint_data['totalEndpoints']} endpoints.")
    print(f"Total endpoints across all services: {total_endpoints}")


def main():
    for service in SERVICES:
        url = BASE_URL.format(service)
        print(f"Fetching Swagger JSON for: {service} -> {url}")
        if service == "reports":
            url = url.replace("docs", "api")
        swagger_data = fetch_swagger_json(url)
        endpoint_data = extract_endpoints(swagger_data)
        save_to_json(service, endpoint_data)


if __name__ == "__main__":
    main()
