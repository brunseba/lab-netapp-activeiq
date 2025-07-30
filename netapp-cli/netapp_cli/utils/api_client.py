"""NetApp ActiveIQ API client."""

import base64
import json
import time
from typing import Dict, Any, Optional, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from rich.console import Console

from netapp_cli.utils.config import NetAppConfig

console = Console()


class NetAppAPIError(Exception):
    """NetApp API error."""

    def __init__(self, message: str, status_code: int = None, response: Dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class NetAppAPIClient:
    """NetApp ActiveIQ API client."""

    def __init__(self, config: NetAppConfig, verbose: bool = False):
        self.config = config
        self.verbose = verbose
        self.base_url = f"https://{config.host}"
        self.session = requests.Session()

        # Set up authentication
        auth_string = f"{config.username}:{config.password}"
        auth_bytes = auth_string.encode('ascii')
        auth_header = base64.b64encode(auth_bytes).decode('ascii')

        self.session.headers.update({
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

        # Configure retry strategy
        try:
            # Try new parameter name first (urllib3 >= 1.26.0)
            retry_strategy = Retry(
                total=3,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"],
                backoff_factor=1
            )
        except TypeError:
            # Fallback to old parameter name for older urllib3 versions
            retry_strategy = Retry(
                total=3,
                status_forcelist=[429, 500, 502, 503, 504],
                method_whitelist=["HEAD", "GET", "OPTIONS"],
                backoff_factor=1
            )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # SSL verification
        self.session.verify = config.verify_ssl

        if not config.verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to NetApp API."""

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        if self.verbose:
            console.print(f"[dim]{method.upper()} {url}[/dim]")
            if params:
                console.print(f"[dim]Params: {params}[/dim]")
            if data:
                console.print(f"[dim]Data: {json.dumps(data, indent=2)}[/dim]")

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=self.config.timeout,
                headers=headers or {}
            )

            if self.verbose:
                console.print(f"[dim]Response: {response.status_code}[/dim]")

            # Handle different response types
            if response.status_code == 204:  # No Content
                return {"success": True}

            try:
                response_data = response.json()
            except ValueError:
                response_data = {"text": response.text}

            if response.status_code >= 400:
                error_message = self._extract_error_message(response_data, response.status_code)
                raise NetAppAPIError(
                    error_message,
                    status_code=response.status_code,
                    response=response_data
                )

            return response_data

        except requests.exceptions.RequestException as e:
            raise NetAppAPIError(f"Request failed: {str(e)}")

    def _extract_error_message(self, response_data: Dict, status_code: int) -> str:
        """Extract error message from API response."""
        if isinstance(response_data, dict):
            # Common error message fields
            error_fields = ["message", "error", "detail", "description"]
            for field in error_fields:
                if field in response_data:
                    return response_data[field]

            # Check for nested error objects
            if "error" in response_data and isinstance(response_data["error"], dict):
                for field in error_fields:
                    if field in response_data["error"]:
                        return response_data["error"][field]

        return f"HTTP {status_code}: {response_data}"

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request."""
        return self._make_request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request."""
        return self._make_request("POST", endpoint, data=data)

    def patch(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make PATCH request."""
        return self._make_request("PATCH", endpoint, data=data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request."""
        return self._make_request("DELETE", endpoint)

    def test_connection(self) -> bool:
        """Test API connection."""
        try:
            result = self.get("/api/cluster")
            return True
        except NetAppAPIError:
            return False

    def wait_for_job(self, job_key: str, timeout: int = 300) -> Dict[str, Any]:
        """Wait for a job to complete."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                job_status = self.get(f"/management-server/jobs/{job_key}")

                if self.verbose:
                    console.print(f"[dim]Job {job_key} status: {job_status.get('state', 'unknown')}[/dim]")

                state = job_status.get("state")
                if state == "COMPLETED":
                    return job_status
                elif state in ["FAILED", "CANCELLED"]:
                    error_msg = job_status.get("message", "Job failed")
                    raise NetAppAPIError(f"Job failed: {error_msg}", response=job_status)

                time.sleep(2)  # Wait 2 seconds before next check

            except NetAppAPIError as e:
                if e.status_code == 404:
                    raise NetAppAPIError(f"Job {job_key} not found")
                raise

        raise NetAppAPIError(f"Job {job_key} timed out after {timeout} seconds")

    def paginate(self, endpoint: str, params: Optional[Dict] = None, max_records: int = None) -> List[Dict]:
        """Paginate through API results."""
        all_records = []
        offset = 0
        limit = 100  # Default page size

        params = params or {}

        while True:
            page_params = params.copy()
            page_params.update({
                "offset": offset,
                "limit": limit
            })

            if max_records and offset >= max_records:
                break

            response = self.get(endpoint, params=page_params)
            records = response.get("records", [])

            if not records:
                break

            all_records.extend(records)

            # Check if we have more records
            num_records = response.get("num_records", 0)
            if len(records) < limit or offset + len(records) >= num_records:
                break

            offset += limit

            if max_records and len(all_records) >= max_records:
                all_records = all_records[:max_records]
                break

        return all_records
