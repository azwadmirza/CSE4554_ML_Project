def install_updates(guid=None):
    """
    Installs updates that match the passed criteria. It may be easier to use the
    list_updates function and set install=True.

    :param guid: list
        A list of GUIDs to be installed

    :return: dict
        A dictionary containing the details about the installed updates

    CLI Examples:

    .. code-block:: bash

        # Normal Usage
        salt '*' win_wua.install_updates
         guid=['12345678-abcd-1234-abcd-1234567890ab',
         '87654321-dcba-4321-dcba-ba0987654321']
    """
    # Check for empty GUID
    if guid is None:
        return 'No GUID Specified'

    # Initialize the PyCom system
    pythoncom.CoInitialize()

    # Create a session with the Windows Update Agent
    wua_session = win32com.client.Dispatch('Microsoft.Update.Session')
    wua_session.ClientApplicationID = 'Salt: Install Update'

    # Create the Searcher, Downloader, Installer, and Collections
    wua_searcher = wua_session.CreateUpdateSearcher()
    wua_download_list = win32com.client.Dispatch('Microsoft.Update.UpdateColl')
    wua_downloader = wua_session.CreateUpdateDownloader()
    wua_install_list = win32com.client.Dispatch('Microsoft.Update.UpdateColl')
    wua_installer = wua_session.CreateUpdateInstaller()

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
    log.debug('Found the following update:')
    ret['Updates'] = {}
    for update in wua_search_result.Updates:
        # Check to see if the update is already installed
        ret['Updates'][update.Identity.UpdateID] = {}
        ret['Updates'][update.Identity.UpdateID]['Title'] = update.Title
        if update.IsInstalled:
            log.debug('Already Installed: {0}'.format(update.Identity.UpdateID))
            log.debug(u'\tTitle: {0}'.format(update.Title))
            ret['Updates'][update.Identity.UpdateID]['AlreadyInstalled'] = True
        # Make sure the EULA has been accepted
        if not update.EulaAccepted:
            log.debug(u'Accepting EULA: {0}'.format(update.Title))
            update.AcceptEula()  # pylint: disable=W0104
        # Add to the list of updates that need to be downloaded
        if update.IsDownloaded:
            log.debug('Already Downloaded: {0}'.format(update.Identity.UpdateID))
            log.debug(u'\tTitle: {0}'.format(update.Title))
            ret['Updates'][update.Identity.UpdateID]['AlreadyDownloaded'] = True
        else:
            log.debug('To Be Downloaded: {0}'.format(update.Identity.UpdateID))
            log.debug(u'\tTitle: {0}'.format(update.Title))
            ret['Updates'][update.Identity.UpdateID]['AlreadyDownloaded'] = False
            wua_download_list.Add(update)

    # Download the updates
    if wua_download_list.Count == 0:
        # Not necessarily a failure, perhaps the update has been downloaded
        # but not installed
        log.debug('No updates to download')
    else:
        # Otherwise, download the update
        log.debug('Downloading...')
        wua_downloader.Updates = wua_download_list

        try:
            wua_downloader.Download()
            log.debug('Download Complete')

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
            ret['location'] = 'Download Section of install_updates'
            ret['file'] = 'win_wua.py'

            return ret

    # Install the updates
    for update in wua_search_result.Updates:
        # Make sure the update has actually been downloaded
        if update.IsDownloaded:
            log.debug(u'To be installed: {0}'.format(update.Title))
            wua_install_list.Add(update)

    if wua_install_list.Count == 0:
        # There are not updates to install
        # This would only happen if there was a problem with the download
        # If this happens often, perhaps some error checking for the download
        log.debug('No updates to install')
        ret['Success'] = False
        ret['Message'] = 'No Updates to install'
        return ret

    wua_installer.Updates = wua_install_list

    # Try to run the installer
    try:
        result = wua_installer.Install()

    except Exception as error:

        # See if we know the problem, if not return the full error
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
        ret['location'] = 'Install Section of install_updates'
        ret['file'] = 'win_wua.py'

        return ret

    rc = {0: 'Installation Not Started',
          1: 'Installation In Progress',
          2: 'Installation Succeeded',
          3: 'Installation Succeeded With Errors',
          4: 'Installation Failed',
          5: 'Installation Aborted'}
    log.debug(rc[result.ResultCode])

    if result.ResultCode in [2, 3]:
        ret['Success'] = True
        ret['NeedsReboot'] = result.RebootRequired
        log.debug('NeedsReboot: {0}'.format(result.RebootRequired))
    else:
        ret['Success'] = False

    ret['Message'] = rc[result.ResultCode]
    rb = {0: 'Never Reboot',
          1: 'Always Reboot',
          2: 'Poss Reboot'}
    for i in range(wua_install_list.Count):
        uid = wua_install_list.Item(i).Identity.UpdateID
        ret['Updates'][uid]['Result'] = rc[result.GetUpdateResult(i).ResultCode]
        ret['Updates'][uid]['RebootBehavior'] = rb[wua_install_list.Item(i).InstallationBehavior.RebootBehavior]

    return ret