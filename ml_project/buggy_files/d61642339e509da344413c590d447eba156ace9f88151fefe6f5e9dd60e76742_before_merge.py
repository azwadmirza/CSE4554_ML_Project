def _get_error(error):
    # Converts boto exception to string that can be used to output error.
    error = '\n'.join(error.split('\n')[1:])
    error = xml.fromstring(error)
    code = error[0][1].text
    message = error[0][2].text
    return code, message