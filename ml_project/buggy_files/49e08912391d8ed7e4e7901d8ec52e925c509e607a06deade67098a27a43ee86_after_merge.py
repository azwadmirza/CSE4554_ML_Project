def commit_new_version(version: str):
    """
    Commits the file containing the version number variable with the version number as the commit
    message.

    :param version: The version number to be used in the commit message.
    """

    check_repo()
    commit_message = config.get('semantic_release', 'commit_message')
    message = '{0}\n\n{1}'.format(version, commit_message)

    version_file = config.get('semantic_release', 'version_variable').split(':')[0]
    # get actual path to filename, to allow running cmd from subdir of git root
    version_filepath = PurePath(os.getcwd(), version_file).relative_to(repo.working_dir)

    repo.git.add(str(version_filepath))
    return repo.git.commit(m=message, author="semantic-release <semantic-release>")