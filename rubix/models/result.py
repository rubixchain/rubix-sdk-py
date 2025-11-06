from dataclasses import dataclass

@dataclass
class Response:
    """
    Standard Response structure of Rubix Core
    
    Attributes:
        status (bool): The status of the response.
        message (str): A message providing additional information about the response.
        result (str | dict | None): The result data of the response, which can be a string, a dictionary, or None.
    """
    status: bool
    message: str
    result: str | dict | None

