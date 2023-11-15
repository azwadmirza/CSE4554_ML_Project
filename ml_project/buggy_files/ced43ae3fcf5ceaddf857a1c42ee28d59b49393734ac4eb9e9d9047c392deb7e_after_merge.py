def promptNewPass():
    password = getpass.getpass("New password:")
    verify = getpass.getpass("Verify password:")
    if (password != verify):
        sys.exit(exits['passwordMatch'])
    return pbkdf2_sha256.encrypt(password, rounds=rounds, salt_size=saltLength)