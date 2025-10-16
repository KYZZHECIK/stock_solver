from typing import Any

class APIError(Exception):
    """Base class for all Alpha Vantage API errors."""
    
    def __init__(self, message: str, data: Any):
        super().__init__()
        self.message = message
        self.data = data
    
    def __str__(self):
        return f"{self.message}. Response = {self.data}"