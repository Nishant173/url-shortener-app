import traceback

from rest_framework import exceptions, status
from rest_framework.response import Response


def api_exception_handler():
    def inner_function(func):
        def wrapper(request, *args, **kwargs):
            try:
                return func(request, *args, **kwargs)
            except exceptions.ValidationError as e:
                response_data = {
                    "detail": e.detail,
                    "code": e.default_code,
                }
                return Response(data=response_data, status=e.status_code)
            except Exception as e:
                response_data = {
                    "message": "Internal server error - Something went wrong",
                    "error_type": type(e).__name__,
                    "error_msg": str(e),
                    "error_trace": traceback.format_exc(),
                }
                return Response(data=response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return wrapper
    return inner_function

