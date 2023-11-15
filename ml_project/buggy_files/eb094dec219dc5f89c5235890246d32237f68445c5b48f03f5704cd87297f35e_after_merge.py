def capfuzz_start(request):
    """Start CapFuzz UI"""
    logger.info("Starting CapFuzz Web UI")
    try:
        stop_capfuzz(settings.PORT)
        start_fuzz_ui(settings.PORT)
        time.sleep(3)
        logger.info("CapFuzz UI Started")
        if request.GET['project']:
            project = request.GET['project']
        else:
            project = ""
        return HttpResponseRedirect('http://localhost:' + str(settings.PORT) + "/dashboard/" + project)
    except:
        PrintException("Starting CapFuzz Web UI")
        return print_n_send_error_response(request, "Error Starting CapFuzz UI")