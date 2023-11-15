def whitelistExport(force=None, path=None):
    file = request.files['file']
    filename = secure_filename(file.filename)
    force = request.form.get('force')
    if (force=="df") and (os.path.isfile(filename)):
        status=["wl_file_already_exists","warning"]
    else:
        if(os.path.isfile(filename)):
            os.remove(filename)
        exportWhitelist(filename)
        status=["wl_exported","success"]
    return render_template('admin.html', status=status)