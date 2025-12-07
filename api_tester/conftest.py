import pytest
import time
import httpx
import os

@pytest.fixture(scope="session")
def api_url():
    return os.getenv("API_URL", "http://localhost:8000")

@pytest.fixture(scope="session", autouse=True)
def wait_for_api(api_url):
    print(f"\nWaiting for {api_url}/health/ready...")
    timeout = 60
    start = time.time()
    ready = False
    
    with httpx.Client() as client:
        while time.time() - start < timeout:
            try:
                res = client.get(f"{api_url}/health/ready")
                if res.status_code == 200:
                    ready = True
                    break
            except httpx.RequestError:
                pass
            time.sleep(1)
    
    if not ready:
        pytest.fail(f"API at {api_url} not ready within {timeout}s")

@pytest.fixture
def http_client(api_url):
    with httpx.Client(base_url=api_url) as client:
        yield client
