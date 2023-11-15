def blacklistExport():
    file = request.files['file']
    filename = secure_filename(file.filename)
    force = request.form.get('force')
    if (force=="df") and (os.path.isfile(filename)):
        status=["bl_file_already_exists","warning"]
    else:
        if(os.path.isfile(filename)):
            os.remove(filename)
        exportBlacklist(filename)
        status=["bl_exported","success"]
    return render_template('admin.html', status=status)