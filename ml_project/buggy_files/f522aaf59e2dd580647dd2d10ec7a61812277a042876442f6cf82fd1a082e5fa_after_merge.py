def blacklistImport():
    file = request.files['file']
    force = request.form.get('force')
    count = countBlacklist()
    if (count == 0) | (not count) | (force == "f"):
        dropBlacklist()
        importBlacklist(TextIOWrapper(file.stream))
        status=["bl_imported","success"]
    else:
        status=["bl_already_filled","info"]
    return render_template('admin.html', status=status)