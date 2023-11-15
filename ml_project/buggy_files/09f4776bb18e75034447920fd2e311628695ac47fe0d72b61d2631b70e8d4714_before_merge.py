def chowner(path, owner):
    owner_info = pwd.getpwnam(owner)
    os.chown(path, owner_info[2], owner_info[3])