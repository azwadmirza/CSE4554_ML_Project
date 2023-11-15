def masterLogin():
    master = input("Master account username: ")
    masterPass = hashlib.sha256(bytes(getpass.getpass("Master password:"), "utf-8")).hexdigest()
    if collection.find({'username':master, 'password':masterPass, 'master':True}).count()==0:
        sys.exit('Master user/password combination does not exist')
    return True