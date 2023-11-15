def download(request):
    """
    Download from MobSF Route
    """
    msg = "Error Downloading File "
    if request.method == 'GET':
        allowed_exts = settings.ALLOWED_EXTENSIONS
        filename = request.path.replace("/download/", "", 1)
        # Security Checks
        if "../" in filename:
            return print_n_send_error_response(request, "Path Traversal Attack detected")
        ext = os.path.splitext(filename)[1]
        if ext in allowed_exts:
            dwd_file = os.path.join(settings.DWD_DIR, filename)
            if os.path.isfile(dwd_file):
                wrapper = FileWrapper(open(dwd_file, "rb"))
                response = HttpResponse(
                    wrapper, content_type=allowed_exts[ext])
                response['Content-Length'] = os.path.getsize(dwd_file)
                return response
    msg += filename
    return print_n_send_error_response(request, msg)