class GaleneError(Exception):
    """Base class for all Galene SDK errors."""
    pass


class GaleneHttpError(GaleneError):
    """Base class for errors returned by the Galene API."""

    def __init__(self, message: str, status_code: int = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details

    def __str__(self):
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class GaleneBadRequestError(GaleneHttpError):
    """HTTP 400 - The request was invalid."""
    pass


class GaleneUnauthorizedError(GaleneHttpError):
    """HTTP 401 - Authentication required or failed."""
    pass


class GaleneForbiddenError(GaleneHttpError):
    """HTTP 403 - The authenticated user does not have permission."""
    pass


class GaleneNotFoundError(GaleneHttpError):
    """HTTP 404 - The requested resource (group, user, token) was not found."""
    pass


class GaleneConflictError(GaleneHttpError):
    """
    HTTP 412 - Precondition Failed.
    Used for ETag/concurrency conflicts when updating resources.
    """
    pass


class GaleneServerError(GaleneHttpError):
    """HTTP 5xx - The Galene server encountered an internal error."""
    pass
