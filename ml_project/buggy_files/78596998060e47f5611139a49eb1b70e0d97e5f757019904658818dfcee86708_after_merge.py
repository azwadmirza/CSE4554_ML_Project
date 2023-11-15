def updateDatabaseOnEdit(ID,newPath):
    sqlCheckPath = newPath if newPath[-1] == '/' else newPath + u'/'
    storedPathName = session.query(GdriveId).filter(GdriveId.gdrive_id == ID).first()
    if storedPathName:
        storedPathName.path = sqlCheckPath
        session.commit()