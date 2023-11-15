def clip_dump(request):
    """Dump Android ClipBoard"""
    logger.info("Starting Clipboard Dump Service in VM/Device")
    try:
        data = {}
        if request.method == 'POST':
            adb = getADB()
            args = ["am",
                    "startservice",
                    "opensecurity.clipdump/.ClipDumper"]
            try:
                adb_command(args, True)
                data = {'status': 'success'}
            except:
                PrintException("[ERROR] Dumping Clipboard")
                data = {'status': 'error'}
        else:
            data = {'status': 'failed'}
        return HttpResponse(json.dumps(data), content_type='application/json')
    except:
        PrintException("[ERROR] Dumping Clipboard")
        return HttpResponseRedirect('/error/')