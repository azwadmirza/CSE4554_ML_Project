def download(request):
    """
    Download from MobSF Route
    """
    try:
        if request.method == 'GET':
            allowed_exts = settings.ALLOWED_EXTENSIONS
            filename = request.path.replace("/download/", "", 1)
            # Security Checks
            if "../" in filename:
                logger.info("\n[ATTACK] Path Traversal Attack detected")
                return HttpResponseRedirect('/error/')
            ext = os.path.splitext(filename)[1]
            if ext in allowed_exts:
                dwd_file = os.path.join(settings.DWD_DIR, filename)
                if os.path.isfile(dwd_file):
                    wrapper = FileWrapper(open(dwd_file, "rb"))
                    response = HttpResponse(
                        wrapper, content_type=allowed_exts[ext])
                    response['Content-Length'] = os.path.getsize(dwd_file)
                    return response
    except:
        PrintException("Error Downloading File")
    return HttpResponseRedirect('/error/')