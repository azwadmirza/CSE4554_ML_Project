def whitelistImport(force=None, path=None):
    file = request.files['file']
    force = request.form.get('force')
    count = countWhitelist()
    if (count == 0) | (not count) | (force == "f"):
        dropWhitelist()
        importWhitelist(TextIOWrapper(file.stream))
        status=["wl_imported","success"]
    else:
        status=["wl_already_filled","info"]
    return render_template('admin.html', status=status)