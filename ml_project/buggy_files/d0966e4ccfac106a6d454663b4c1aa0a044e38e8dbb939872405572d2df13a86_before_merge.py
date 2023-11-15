def get_github_repo(organization, repo, gh=None):
    """Return the github repository.

    :param organization:
    :type organization: string
    :param repo:
    :type repo: string
    :param gh:
    :type gh: Github
    :return:
    :rtype github.Repository.Repository
    """
    try:
        gh = gh or github.MainClass.Github(user_agent='Medusa')
        return gh.get_organization(organization).get_repo(repo)
    except github.GithubException as e:
        logger.debug('Unable to contact Github: {ex!r}', ex=e)
        raise