def commit_new_version(version: str):
    """
    Commits the file containing the version number variable with the version number as the commit
    message.

    :param version: The version number to be used in the commit message.
    """

    check_repo()
    commit_message = config.get('semantic_release', 'commit_message')
    message = '{0}\n\n{1}'.format(version, commit_message)
    repo.git.add(config.get('semantic_release', 'version_variable').split(':')[0])
    return repo.git.commit(m=message, author="semantic-release <semantic-release>")