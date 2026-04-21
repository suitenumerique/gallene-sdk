import pytest
from galene.api.exceptions import (
    GaleneError,
    GaleneHttpError,
    GaleneBadRequestError,
    GaleneUnauthorizedError,
    GaleneForbiddenError,
    GaleneNotFoundError,
    GaleneConflictError,
    GaleneServerError
)

def test_exception_inheritance():
    assert issubclass(GaleneHttpError, GaleneError)
    assert issubclass(GaleneBadRequestError, GaleneHttpError)
    assert issubclass(GaleneUnauthorizedError, GaleneHttpError)
    assert issubclass(GaleneForbiddenError, GaleneHttpError)
    assert issubclass(GaleneNotFoundError, GaleneHttpError)
    assert issubclass(GaleneConflictError, GaleneHttpError)
    assert issubclass(GaleneServerError, GaleneHttpError)

def test_exception_message():
    err = GaleneError("test message")
    assert str(err) == "test message"

def test_http_exception_formatting():
    # Without status code
    err = GaleneHttpError("failed")
    assert str(err) == "failed"
    
    # With status code
    err = GaleneHttpError("not found", status_code=404)
    assert str(err) == "[404] not found"
    assert err.status_code == 404

def test_http_exception_details():
    details = {"reason": "missing param"}
    err = GaleneBadRequestError("bad request", status_code=400, details=details)
    assert err.details == details
    assert str(err) == "[400] bad request"

def test_specific_exceptions():
    with pytest.raises(GaleneNotFoundError) as excinfo:
        raise GaleneNotFoundError("missing", status_code=404)
    
    assert excinfo.value.status_code == 404
    assert "missing" in str(excinfo.value)
