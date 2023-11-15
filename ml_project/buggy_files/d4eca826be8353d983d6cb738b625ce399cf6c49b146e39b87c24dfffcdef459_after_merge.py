def moveGdriveFolderRemote(origin_file, target_folder):
    drive = getDrive(Gdrive.Instance().drive)
    previous_parents = ",".join([parent["id"] for parent in origin_file.get('parents')])
    children = drive.auth.service.children().list(folderId=previous_parents).execute()
    gFileTargetDir = getFileFromEbooksFolder(None, target_folder)
    if not gFileTargetDir:
        # Folder is not existing, create, and move folder
        gFileTargetDir = drive.CreateFile(
            {'title': target_folder, 'parents': [{"kind": "drive#fileLink", 'id': getEbooksFolderId()}],
             "mimeType": "application/vnd.google-apps.folder"})
        gFileTargetDir.Upload()
    # Move the file to the new folder
    drive.auth.service.files().update(fileId=origin_file['id'],
                                      addParents=gFileTargetDir['id'],
                                      removeParents=previous_parents,
                                      fields='id, parents').execute()
    # if previous_parents has no childs anymore, delete original fileparent
    if len(children['items']) == 1:
        deleteDatabaseEntry(previous_parents)
        drive.auth.service.files().delete(fileId=previous_parents).execute()