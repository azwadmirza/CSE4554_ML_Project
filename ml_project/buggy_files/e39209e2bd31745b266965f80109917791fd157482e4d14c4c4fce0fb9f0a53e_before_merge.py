def _format_response(response, msg):
    if 'Error' in response:
        msg = 'Error'

    return {
        msg: response.replace('\n', '')
    }