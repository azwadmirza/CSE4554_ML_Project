def existsInDB(user):
    return True if collection.find({'username':username}).count()>0 else False