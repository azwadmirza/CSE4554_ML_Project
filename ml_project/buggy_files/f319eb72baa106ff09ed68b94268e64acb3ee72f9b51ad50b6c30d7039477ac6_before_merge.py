def download_updates(skips=None, retries=5, categories=None):
    '''
    Downloads all available updates, skipping those that require user
    interaction.

    Various aspects of the updates can be included or excluded. this feature is
    still in development.

    retries
        Number of retries to make before giving up. This is total, not per
        step.

    categories
        Specify the categories to update. Must be passed as a list.

        .. code-block:: bash

            salt '*' win_update.download_updates categories="['Updates']"

        Categories include the following:

        * Updates
        * Windows 7
        * Critical Updates
        * Security Updates
        * Update Rollups

    CLI Examples:

    .. code-block:: bash

        # Normal Usage
        salt '*' win_update.download_updates

        # Download critical updates only
        salt '*' win_update.download_updates categories="['Critical Updates']"

    '''

    log.debug('categories to search for are: {0}'.format(str(categories)))
    quidditch = PyWinUpdater(skipDownloaded=True)
    quidditch.SetCategories(categories)
    quidditch.SetSkips(skips)

    # this is where we be seeking the things! yar!
    comment, passed, retries = _search(quidditch, retries)
    if not passed:
        return (comment, str(passed))

    # this is where we get all the things! i.e. download updates.
    comment, passed, retries = _download(quidditch, retries)
    if not passed:
        return (comment, str(passed))

    try:
        comment = quidditch.GetDownloadResults()
    except Exception as exc:
        comment = 'could not get results, but updates were installed. {0}'.format(exc)
    return 'Windows is up to date. \n{0}'.format(comment)