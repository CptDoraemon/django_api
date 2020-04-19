from rest_framework.views import exception_handler
from response_templates.templates import error_template
from rest_framework.exceptions import ValidationError, AuthenticationFailed


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is None:
        return response

    if isinstance(exc, ValidationError):
        '''
        {
            field: [str],
            field: [str]
        }
        '''
        # flatten to a string message
        try:
            data = response.data
            first_key = list(data.keys())[0]
            first_value = data[first_key][0]  # it's a list
            message = "{0}: {1}".format(first_key.capitalize(), first_value.capitalize())
            response.data = error_template(message)
        except (KeyError, AttributeError):
            response.data = error_template('Validation error')

    if isinstance(exc, AuthenticationFailed):
        try:
            response.data = error_template(response.data['detail'])
        except KeyError:
            response.data = error_template('Authentication Failed')

    # rest cases:
    try:
        response.data = error_template(response.data['detail'])
    except KeyError:
        pass

    return response