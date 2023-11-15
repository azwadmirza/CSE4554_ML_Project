def print_n_send_error_response(request, msg, api=False, exp='Error Description'):
    """Print and log errors"""
    logger.error(msg)
    if api:
        api_response = {"error": msg}
        return api_response
    else:
        context = {
            'title': 'Error',
            'exp': exp,
            'doc': msg
        }
        template = "general/error.html"
        return render(request, template, context, status=500)