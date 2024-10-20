import os
import requests
import socket

# Get environment variables or defaults
SD_URL = os.getenv('SD_URL', 'http://localhost:8080/register')
SERVICE_TYPE = os.getenv('SERVICE_TYPE', 'unknown')

# Function to get the IP address of the host
def get_host_ip():
    try:
        host_ip = socket.gethostbyname(socket.gethostname())
        return host_ip
    except Exception as e:
        print(f"Error getting host IP: {e}")
        return None
    
# Register the service with the service discovery
def register_service():
    host_ip = get_host_ip()

    if not host_ip:
        print("Failed to get host IP. Service registration aborted.")
        return

    payload = {
        "host": host_ip,
        "type": SERVICE_TYPE
    }

    try:
        response = requests.post(SD_URL, json=payload)
        if response.status_code == 200:
            print(f"Service successfully registered: {host_ip} as {SERVICE_TYPE}")
        else:
            print(f"Failed to register service. Status code: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error registering service: {e}")

if __name__ == '__main__':
    register_service()