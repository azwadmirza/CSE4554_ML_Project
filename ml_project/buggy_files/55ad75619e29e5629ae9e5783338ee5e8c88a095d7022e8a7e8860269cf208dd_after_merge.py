def masterLogin():
    master = input("Master account username: ")
    if verifyPass(getpass.getpass("Master password:"), master):
        if collection.find({'username':master, 'master':True}).count()==0:
            sys.exit(exits['noMaster'])
    else:
        sys.exit('Master user/password combination does not exist')
    return True