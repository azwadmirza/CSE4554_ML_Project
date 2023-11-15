def blacklistImport():
    path = request.form.get('file')
    force = request.form.get('force')
    if (matchFilePath(path)):
        if os.path.isfile(path):
            count = countBlacklist()
            if (count == 0) | (not count) | (force == "f"):
                dropBlacklist()
                importBlacklist(path)
                status=["bl_imported","success"]
            else:
                status=["bl_already_filled","info"]
        else:
            status=["invalid_path","error"]
    else:
        status=["invalid_path_format","error"]
    return render_template('admin.html', status=status)