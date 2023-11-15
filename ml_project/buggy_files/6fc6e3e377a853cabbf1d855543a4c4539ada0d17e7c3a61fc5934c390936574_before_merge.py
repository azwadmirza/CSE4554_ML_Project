def whitelistImport(force=None, path=None):
    path = request.form.get('file')
    force = request.form.get('force')
    if (matchFilePath(path)):
        if os.path.isfile(path):
            count = countWhitelist()
            if (count == 0) | (not count) | (force == "f"):
                dropWhitelist()
                importWhitelist(path)
                status=["wl_imported","success"]
            else:
                status=["wl_already_filled","info"]
        else:
            status=["invalid_path","error"]
    else:
        status=["invalid_path_format","error"]
    return render_template('admin.html', status=status)