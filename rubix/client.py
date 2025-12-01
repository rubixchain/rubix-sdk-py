import requests
from typing import Dict, Any, Optional
from urllib.parse import urljoin

class RubixClient:
    def __init__(
            self, 
            node_url: str = "http://localhost:20000", 
            timeout: int = 300,
            api_key: Optional[str] = None
        ):
        """
        Initialize Rubix client.
        
        Args:
            node_url: Base URL of the Rubix node
            timeout: Request timeout in seconds (default: 300)
            api_key (str, Optional): API Key passed in request header
        """
        
        self.node_url = node_url.rstrip('/')  # Remove trailing slash
        self._timeout = timeout
        self._api_key = api_key
    
    def _make_get_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Protected method to make GET request to Rubix node.
        
        Args:
            endpoint: API endpoint path
            params: Optional query parameters as dictionary
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.exceptions.RequestException: If request fails
            ValueError: If response is not valid JSON
        """
        # Build full URL
        url = urljoin(self.node_url, endpoint)
        
        try:
            response = requests.get(
                url,
                params=params,
                timeout=self._timeout
            )
            
            # Raise for HTTP errors (4xx, 5xx)
            response.raise_for_status()
            
            # Parse and return JSON
            return response.json()
            
        except requests.exceptions.Timeout:
            raise requests.exceptions.RequestException(
                f"GET request to {url} timed out after {self._timeout}s"
            )
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.RequestException(
                f"Failed to connect to Rubix node at {url}"
            )
        except ValueError as e:
            raise ValueError(f"Invalid JSON response from {url}: {e}")
    
    def _make_post_request(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Protected method to make POST request to Rubix node.
        
        Args:
            endpoint: API endpoint path (e.g., "/api/request-did-for-pubkey")
            json_data: Optional JSON body data as dictionary
            params: Optional query parameters as dictionary
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.exceptions.RequestException: If request fails
            ValueError: If response is not valid JSON
        """
        # Build full URL
        url = urljoin(self.node_url, endpoint)
        
        # Add headers
        headers: Dict[str, str] = {}
        if self._api_key:
            headers["X-API-Key"] = self._api_key

        try:
            response = requests.post(
                url,
                json=json_data,
                params=params,
                timeout=self._timeout,
                headers=headers
            )
            
            # Raise for HTTP errors (4xx, 5xx)
            response.raise_for_status()
            
            # Parse and return JSON
            return response.json()
            
        except requests.exceptions.Timeout:
            raise requests.exceptions.RequestException(
                f"POST request to {url} timed out after {self._timeout}s"
            )
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.RequestException(
                f"Failed to connect to Rubix node at {url}"
            )
        except ValueError as e:
            raise ValueError(f"Invalid JSON response from {url}: {e}")

    def _make_form_data_request(
        self,
        endpoint: str,
        files: Any = None,
        data: Any = None,
        params: Any = None
    ) -> Any:
        """
        Protected method to make multipart/form-data POST request to Rubix node.
        
        Args:
            endpoint: API endpoint path (e.g., "/api/upload")
            files: Dictionary of files to upload. Can be:
                - {'field_name': file_object}
                - {'field_name': ('filename', file_object)}
                - {'field_name': ('filename', file_object, 'content_type')}
            data: Dictionary of form fields (non-file data)
            params: Optional query parameters as dictionary
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.exceptions.RequestException: If request fails
            ValueError: If response is not valid JSON
        """
        # Build full URL
        url = urljoin(self.node_url, endpoint)

        # Add Headers
        headers: Dict[str, str] = {}
        if self._api_key:
            headers["X-API-Key"] = self._api_key

        try:
            response = requests.post(
                url,
                files=files,
                data=data,
                params=params,
                timeout=self._timeout,
                headers=headers
            )
            
            # Raise for HTTP errors (4xx, 5xx)
            response.raise_for_status()
            
            # Parse and return JSON
            return response.json()
            
        except requests.exceptions.Timeout:
            raise requests.exceptions.RequestException(
                f"Form-data POST request to {url} timed out after {self._timeout}s"
            )
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.RequestException(
                f"Failed to connect to Rubix node at {url}"
            )
        except ValueError as e:
            raise ValueError(f"Invalid JSON response from {url}: {e}")