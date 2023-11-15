def deploy():
    print("Current head:  ", HEAD)
    print("Current master:", MASTER)

    if not tools.is_ancestor(HEAD, MASTER):
        print("Not deploying due to not being on master")
        sys.exit(0)

    if "PYPI_TOKEN" not in os.environ:
        print("Running without access to secure variables, so no deployment")
        sys.exit(0)

    tools.configure_git()

    for project in tools.all_projects():
        do_release(project)

    sys.exit(0)