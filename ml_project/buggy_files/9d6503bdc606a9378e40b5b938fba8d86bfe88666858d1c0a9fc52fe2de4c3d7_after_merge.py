def existsInDB(user):
    return True if collection.find({'username':user}).count()>0 else False