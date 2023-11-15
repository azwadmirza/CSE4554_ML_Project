def deploy():
    print("Current head:  ", HEAD)
    print("Current master:", MASTER)

    if not tools.is_ancestor(HEAD, MASTER):
        print("Not deploying due to not being on master")
        sys.exit(0)

    if not tools.has_travis_secrets():
        print("Running without access to secure variables, so no deployment")
        sys.exit(0)

    print("Decrypting secrets")
    tools.decrypt_secrets()
    tools.configure_git()

    for project in tools.all_projects():
        do_release(project)

    sys.exit(0)