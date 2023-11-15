def export(
    name,
    target=None,
    rev=None,
    user=None,
    username=None,
    password=None,
    force=False,
    overwrite=False,
    externals=True,
    trust=False,
    trust_failures=None,
):
    """
    Export a file or directory from an SVN repository

    name
        Address and path to the file or directory to be exported.

    target
        Name of the target directory where the checkout will put the working
        directory

    rev : None
        The name revision number to checkout. Enable "force" if the directory
        already exists.

    user : None
        Name of the user performing repository management operations

    username : None
        The user to access the name repository with. The svn default is the
        current user

    password
        Connect to the Subversion server with this password

        .. versionadded:: 0.17.0

    force : False
        Continue if conflicts are encountered

    overwrite : False
        Overwrite existing target

    externals : True
        Change to False to not checkout or update externals

    trust : False
        Automatically trust the remote server. SVN's --trust-server-cert

    trust_failures : None
        Comma-separated list of certificate trust failures, that shall be
        ignored. This can be used if trust=True is not sufficient. The
        specified string is passed to SVN's --trust-server-cert-failures
        option as-is.

        .. versionadded:: 2019.2.0
    """
    ret = {"name": name, "result": True, "comment": "", "changes": {}}
    if not target:
        return _fail(ret, "Target option is required")

    svn_cmd = "svn.export"
    cwd, basename = os.path.split(target)
    opts = tuple()

    if not overwrite and os.path.exists(target) and not os.path.isdir(target):
        return _fail(
            ret, 'The path "{}" exists and is not ' "a directory.".format(target)
        )
    if __opts__["test"]:
        if not os.path.exists(target):
            return _neutral_test(
                ret, ("{} doesn't exist and is set to be checked out.").format(target)
            )
        svn_cmd = "svn.list"
        rev = "HEAD"
        out = __salt__[svn_cmd](cwd, target, user, username, password, *opts)
        return _neutral_test(ret, ("{}").format(out))

    if not rev:
        rev = "HEAD"

    if force:
        opts += ("--force",)

    if externals is False:
        opts += ("--ignore-externals",)

    if trust:
        opts += ("--trust-server-cert",)

    if trust_failures:
        opts += ("--trust-server-cert-failures", trust_failures)

    out = __salt__[svn_cmd](cwd, name, basename, user, username, password, rev, *opts)
    ret["changes"]["new"] = name
    ret["changes"]["comment"] = name + " was Exported to " + target
    ret["comment"] = out

    return ret