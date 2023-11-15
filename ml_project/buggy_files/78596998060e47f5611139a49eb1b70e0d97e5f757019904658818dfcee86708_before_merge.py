def updateDatabaseOnEdit(ID,newPath):
    storedPathName = session.query(GdriveId).filter(GdriveId.gdrive_id == ID).first()
    if storedPathName:
        storedPathName.path = newPath
        session.commit()