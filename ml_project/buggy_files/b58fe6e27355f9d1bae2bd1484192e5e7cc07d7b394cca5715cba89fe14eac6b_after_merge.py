def uploadFileToEbooksFolder(destFile, f):
    drive = getDrive(Gdrive.Instance().drive)
    parent = getEbooksFolder(drive)
    splitDir = destFile.split('/')
    for i, x in enumerate(splitDir):
        if i == len(splitDir)-1:
            existingFiles = drive.ListFile({'q': "title = '%s' and '%s' in parents and trashed = false" %
                                                 (x.replace("'", r"\'"), parent['id'])}).GetList()
            if len(existingFiles) > 0:
                driveFile = existingFiles[0]
            else:
                driveFile = drive.CreateFile({'title': x, 'parents': [{"kind": "drive#fileLink", 'id': parent['id']}],})
            driveFile.SetContentFile(f)
            driveFile.Upload()
        else:
            existingFolder = drive.ListFile({'q': "title = '%s' and '%s' in parents and trashed = false" %
                                                  (x.replace("'", r"\'"), parent['id'])}).GetList()
            if len(existingFolder) == 0:
                parent = drive.CreateFile({'title': x, 'parents': [{"kind": "drive#fileLink", 'id': parent['id']}],
                    "mimeType": "application/vnd.google-apps.folder"})
                parent.Upload()
            else:
                parent = existingFolder[0]