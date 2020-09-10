from rest_framework.response import Response


def build_error_response(error_code, error_message):
    response = Response()
    response.status_code = error_code
    response.data = {
        'errors': [
            {
                'status': error_code,
                'datails': error_message,
            }
        ]
    }
    return response
