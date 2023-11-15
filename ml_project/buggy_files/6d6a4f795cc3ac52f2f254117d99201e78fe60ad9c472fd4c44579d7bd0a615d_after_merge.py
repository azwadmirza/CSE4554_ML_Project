def getpass(prompt="Password: "):
    if not TEST:
        return gp.getpass(bytes(prompt))
    else:
        return py23_input(prompt)