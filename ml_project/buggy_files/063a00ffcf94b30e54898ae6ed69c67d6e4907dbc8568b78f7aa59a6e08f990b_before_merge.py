def isLastAdmin(user):
    if len(list(collection.find({'username':{'$ne':user}, 'master':True}))) == 0:
        sys.exit('This user is the last admin in the database and thus can not be removed')