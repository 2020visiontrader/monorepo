"""
Custom exception handler for consistent error responses
"""
from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.exceptions import (
    PermissionDenied, NotAuthenticated, ValidationError, Throttled
)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent error shape
    {
        "detail": "...",
        "code": "ERROR_CODE",
        "errors"?: [{"field": "...", "message": "...", "code": "..."}]
    }
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response = {
            'detail': str(exc),
            'code': get_error_code(exc),
        }
        
        # Add field-level errors for ValidationError
        if isinstance(exc, ValidationError):
            errors = []
            if hasattr(exc, 'detail'):
                if isinstance(exc.detail, dict):
                    for field, messages in exc.detail.items():
                        if isinstance(messages, list):
                            for msg in messages:
                                errors.append({
                                    'field': str(field),
                                    'message': str(msg),
                                    'code': 'INVALID',
                                })
                        else:
                            errors.append({
                                'field': str(field),
                                'message': str(messages),
                                'code': 'INVALID',
                            })
            if errors:
                custom_response['errors'] = errors
        
        response.data = custom_response
    
    return response


def get_error_code(exc):
    """Map exception to error code"""
    if isinstance(exc, PermissionDenied):
        return 'FORBIDDEN'
    elif isinstance(exc, NotAuthenticated):
        return 'UNAUTHENTICATED'
    elif isinstance(exc, ValidationError):
        return 'VALIDATION_ERROR'
    elif isinstance(exc, Throttled):
        return 'RATE_LIMITED'
    else:
        return 'ERROR'

