def promptNewPass():
    password = getpass.getpass("New password:")
    verify = getpass.getpass("Verify password:")
    if (password != verify):
        sys.exit("The passwords don't match!")
    # generate new salt
    salt = os.urandom(32)
    keyset = {'password':buildPassword(password,salt=salt), 'salt':salt}
    return keyset