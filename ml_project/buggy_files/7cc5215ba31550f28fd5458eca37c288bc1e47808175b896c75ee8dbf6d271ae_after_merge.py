def masterLogin():
    master = input("Master account username: ")
    masterPass = buildPassword(getpass.getpass("Master password:"), user=master)
    if collection.find({'username':master, 'password':masterPass, 'master':True}).count()==0:
        sys.exit('Master user/password combination does not exist')
    return True