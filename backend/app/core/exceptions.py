"""Custom domain exceptions for NEXUS-BTC."""

class NexusException(Exception):
    """Base exception for all NEXUS-BTC domain failures."""
    def __init__(self, message: str, status_code: int = 500, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class IngestionError(NexusException):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message=message, status_code=400, details=details)


class ValidationError(NexusException):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message=message, status_code=422, details=details)


class EntityNotFoundError(NexusException):
    def __init__(self, entity_id: str):
        super().__init__(message=f"Entity '{entity_id}' not found", status_code=404)


class TransactionNotFoundError(NexusException):
    def __init__(self, txid: str):
        super().__init__(message=f"Transaction '{txid}' not found", status_code=404)


class AlertNotFoundError(NexusException):
    def __init__(self, alert_id: str):
        super().__init__(message=f"Alert '{alert_id}' not found", status_code=404)
