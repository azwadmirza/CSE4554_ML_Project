def blacklistExport():
    path = request.form.get('file')
    force = request.form.get('force')
    if (matchFilePath(path)):
        if (force=="df") and (os.path.isfile(path)):
            status=["bl_file_already_exists","warning"]
        else:
            if(os.path.isfile(path)):
                os.remove(path)
            exportBlacklist(path)
            status=["bl_exported","success"]
    else:
        status=["invalid_path","error"]
    return render_template('admin.html', status=status)