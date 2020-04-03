def error_template(message):
    return {
        'status': 'error',
        'message': message
    }


def success_template(message=None, data=None):
    response = {
        'status': 'success',
        'message': message if message else 'operation succeeded',
    }
    if data:
        response['data'] = data.copy()
    return response