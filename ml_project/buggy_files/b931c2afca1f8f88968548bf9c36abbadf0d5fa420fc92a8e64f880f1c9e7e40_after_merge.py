def touch(request):
    """Sending Touch Events"""
    logger.info("Sending Touch Events")
    try:
        data = {}
        if (request.method == 'POST') and (is_number(request.POST['x'])) and (is_number(request.POST['y'])):
            x_axis = request.POST['x']
            y_axis = request.POST['y']
            adb = getADB()
            args = ["input",
                    "tap",
                    x_axis,
                    y_axis]
            data = {'status': 'success'}
            try:
                adb_command(args, True)
            except:
                data = {'status': 'error'}
                PrintException("Performing Touch Action")
        else:
            data = {'status': 'failed'}
        return HttpResponse(json.dumps(data), content_type='application/json')
    except:
        PrintException("Sending Touch Events")
        return print_n_send_error_response(request, "Error Sending Touch Events", True)