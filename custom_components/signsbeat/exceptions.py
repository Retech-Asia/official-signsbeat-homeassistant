"""Exceptions for the Signsbeat integration."""


class SignsbeatApiException(Exception):
    """Exception raised for Signsbeat API errors."""


class SignsbeatAuthException(SignsbeatApiException):
    """Exception raised for Signsbeat authentication errors (401/403)."""
