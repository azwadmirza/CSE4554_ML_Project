def copyToDrive(drive, uploadFile, createRoot, replaceFiles,
        ignoreFiles=None,
        parent=None, prevDir=''):
    ignoreFiles = ignoreFiles or []
    drive = getDrive(drive)
    isInitial = not bool(parent)
    if not parent:
        parent = getEbooksFolder(drive)
    if os.path.isdir(os.path.join(prevDir,uploadFile)):
        existingFolder = drive.ListFile({'q': "title = '%s' and '%s' in parents and trashed = false" % (os.path.basename(uploadFile), parent['id'])}).GetList()
        if len(existingFolder) == 0 and (not isInitial or createRoot):
            parent = drive.CreateFile({'title': os.path.basename(uploadFile), 'parents': [{"kind": "drive#fileLink", 'id': parent['id']}],
                "mimeType": "application/vnd.google-apps.folder"})
            parent.Upload()
        else:
            if (not isInitial or createRoot) and len(existingFolder) > 0:
                parent = existingFolder[0]
        for f in os.listdir(os.path.join(prevDir, uploadFile)):
            if f not in ignoreFiles:
                copyToDrive(drive, f, True, replaceFiles, ignoreFiles, parent, os.path.join(prevDir, uploadFile))
    else:
        if os.path.basename(uploadFile) not in ignoreFiles:
            existingFiles = drive.ListFile({'q': "title = '%s' and '%s' in parents and trashed = false" % (os.path.basename(uploadFile), parent['id'])}).GetList()
            if len(existingFiles) > 0:
                driveFile = existingFiles[0]
            else:
                driveFile = drive.CreateFile({'title': os.path.basename(uploadFile), 'parents': [{"kind":"drive#fileLink", 'id': parent['id']}], })
            driveFile.SetContentFile(os.path.join(prevDir, uploadFile))
            driveFile.Upload()