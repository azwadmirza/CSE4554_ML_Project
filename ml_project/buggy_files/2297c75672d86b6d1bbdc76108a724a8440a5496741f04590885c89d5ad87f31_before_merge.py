def getFile(pathId, fileName, drive):
    metaDataFile = "'%s' in parents and trashed = false and title = '%s'" % (pathId, fileName.replace("'", "\\'"))

    fileList = drive.ListFile({'q': metaDataFile}).GetList()
    if fileList.__len__() == 0:
        return None
    else:
        return fileList[0]