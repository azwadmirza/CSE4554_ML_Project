def download_updates(guid=None):
    """
    Downloads updates that match the list of passed GUIDs. It's easier to use
    this function by using list_updates and setting install=True.

    :param guid:
        A list of GUIDs to be downloaded

    :return:
        A dictionary containing the status, a message, and a list of updates
        that were downloaded.

    CLI Examples:

    .. code-block:: bash

        # Normal Usage
        salt '*' win_wua.download_updates \
                guid=['12345678-abcd-1234-abcd-1234567890ab',\
                      '87654321-dcba-4321-dcba-ba0987654321']
    """
    # Check for empty GUID
    if guid is None:
        return "No GUID Specified"

    # Initialize the PyCom system
    pythoncom.CoInitialize()

    # Create a session with the Windows Update Agent
    wua_session = win32com.client.Dispatch('Microsoft.Update.Session')
    wua_session.ClientApplicationID = 'Salt: Install Update'

    # Create the Searcher, Downloader, Installer, and Collections
    wua_searcher = wua_session.CreateUpdateSearcher()
    wua_download_list = win32com.client.Dispatch('Microsoft.Update.UpdateColl')
    wua_downloader = wua_session.CreateUpdateDownloader()

    ret = {}

    # Searching for the GUID
    search_string = ''
    search_list = ''
    log.debug('Searching for updates:')
    for ident in guid:
        log.debug('{0}'.format(ident))
        if search_string == '':
            search_string = 'UpdateID=\'{0}\''.format(ident.lower())
            search_list = '{0}'.format(ident.lower())
        else:
            search_string += ' or UpdateID=\'{0}\''.format(ident.lower())
            search_list += '\n{0}'.format(ident.lower())

    try:
        wua_search_result = wua_searcher.Search(search_string)
        if wua_search_result.Updates.Count == 0:
            log.debug('No Updates found for:\n\t\t{0}'.format(search_list))
            ret['Success'] = False
            ret['Details'] = 'No Updates found: {0}'.format(search_list)
            return ret
    except Exception:
        log.debug('Invalid Search String: {0}'.format(search_string))
        return 'Invalid Search String: {0}'.format(search_string)

    # List updates found
    log.debug('Found the following updates:')
    ret['Updates'] = {}
    for update in wua_search_result.Updates:
        # Check to see if the update is already installed
        ret['Updates'][update.Identity.UpdateID] = {}
        ret['Updates'][update.Identity.UpdateID]['Title'] = update.Title
        if update.IsInstalled:
            log.debug('Already Installed: {0}'.format(update.Identity.UpdateID))
            log.debug('\tTitle: {0}'.format(update.Title))
            ret['Updates'][update.Identity.UpdateID]['AlreadyInstalled'] = True
        # Make sure the EULA has been accepted
        if not update.EulaAccepted:
            log.debug('Accepting EULA: {0}'.format(update.Title))
            update.AcceptEula  # pylint: disable=W0104
        # Add to the list of updates that need to be downloaded
        if update.IsDownloaded:
            log.debug('Already Downloaded: {0}'.format(update.Identity.UpdateID))
            log.debug('\tTitle: {0}'.format(update.Title))
            ret['Updates'][update.Identity.UpdateID]['AlreadyDownloaded'] = True
        else:
            log.debug('To Be Downloaded: {0}'.format(update.Identity.UpdateID))
            log.debug('\tTitle: {0}'.format(update.Title))
            ret['Updates'][update.Identity.UpdateID]['AlreadyDownloaded'] = False
            wua_download_list.Add(update)

    # Check the download list
    if wua_download_list.Count == 0:
        # Not necessarily a failure, perhaps the update has been downloaded
        log.debug('No updates to download')
        ret['Success'] = False
        ret['Message'] = 'No updates to download'
        return ret

    # Download the updates
    log.debug('Downloading...')
    wua_downloader.Updates = wua_download_list

    try:
        result = wua_downloader.Download()

    except Exception as error:

        ret['Success'] = False
        ret['Result'] = format(error)

        hr, msg, exc, arg = error.args  # pylint: disable=W0633
        # Error codes found at the following site:
        # https://msdn.microsoft.com/en-us/library/windows/desktop/hh968413(v=vs.85).aspx
        fc = {-2145124316: 'No Updates: 0x80240024',
              -2145124284: 'Access Denied: 0x8024044'}
        try:
            failure_code = fc[exc[5]]
        except KeyError:
            failure_code = 'Unknown Failure: {0}'.format(error)

        log.debug('Download Failed: {0}'.format(failure_code))
        ret['error_msg'] = failure_code
        ret['location'] = 'Download Section of download_updates'
        ret['file'] = 'win_wua.py'

        return ret

    log.debug('Download Complete')

    rc = {0: 'Download Not Started',
          1: 'Download In Progress',
          2: 'Download Succeeded',
          3: 'Download Succeeded With Errors',
          4: 'Download Failed',
          5: 'Download Aborted'}
    log.debug(rc[result.ResultCode])

    if result.ResultCode in [2, 3]:
        ret['Success'] = True
    else:
        ret['Success'] = False

    ret['Message'] = rc[result.ResultCode]

    for i in range(wua_download_list.Count):
        uid = wua_download_list.Item(i).Identity.UpdateID
        ret['Updates'][uid]['Result'] = rc[result.GetUpdateResult(i).ResultCode]

    return ret