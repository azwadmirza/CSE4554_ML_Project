def getFolderInFolder(parentId, folderName, drive):
    # drive = getDrive(drive)
    query=""
    if folderName:
        query = "title = '%s' and " % folderName.replace("'", "\\'")
    folder = query + "'%s' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false" % parentId
    fileList = drive.ListFile({'q': folder}).GetList()
    if fileList.__len__() == 0:
        return None
    else:
        return fileList[0]