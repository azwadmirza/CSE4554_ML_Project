def print_n_send_error_response(request, msg, api, exp='Error Description'):
    """Print and log errors"""
    logger.error(Color.BOLD + Color.RED + '[ERROR] ' + msg + Color.END)
    time_stamp = time.time()
    formatted_tms = datetime.datetime.fromtimestamp(
        time_stamp).strftime('%Y-%m-%d %H:%M:%S')
    data = '\n[' + formatted_tms + ']\n[ERROR] ' + msg
    try:
        log_path = settings.LOG_DIR
    except:
        log_path = os.path.join(settings.BASE_DIR, "logs/")
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    with open(os.path.join(log_path, 'MobSF.log'), 'a') as flip:
        flip.write(data)
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