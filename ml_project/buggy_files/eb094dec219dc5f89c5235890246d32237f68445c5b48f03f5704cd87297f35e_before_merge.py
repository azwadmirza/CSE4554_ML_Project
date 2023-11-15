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
        PrintException("[ERROR] Starting CapFuzz Web UI")
        return HttpResponseRedirect('/error/')