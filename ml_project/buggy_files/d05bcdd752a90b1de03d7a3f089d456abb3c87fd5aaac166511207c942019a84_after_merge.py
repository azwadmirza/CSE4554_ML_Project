def execute_adb(request):
    """Execute ADB Commands"""
    logger.info("Executing ADB Commands")
    try:
        if request.method == 'POST':
            data = {}
            cmd = request.POST['cmd']
            resp = "error"
            try:
                resp = adb_command(cmd.split(' '))
            except:
                PrintException("Executing ADB Commands")
            data = {'cmd': 'yes', 'resp': resp.decode("utf8", "ignore")}
            return HttpResponse(json.dumps(data), content_type='application/json')
        else:
            return print_n_send_error_response(request, "Only POST allowed", True)
    except:
        PrintException("Executing ADB Commands")
        return print_n_send_error_response(request, "Error running ADB commands", True)