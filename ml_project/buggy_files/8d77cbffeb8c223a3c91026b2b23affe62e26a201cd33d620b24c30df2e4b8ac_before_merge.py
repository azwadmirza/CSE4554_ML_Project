def create_task_from_xml(name,
                         location='\\',
                         xml_text=None,
                         xml_path=None,
                         user_name='System',
                         password=None):
    r'''
    Create a task based on XML. Source can be a file or a string of XML.

    :param str name: The name of the task. This will be displayed in the task
        scheduler.

    :param str location: A string value representing the location in which to
        create the task. Default is '\\' which is the root for the task
        scheduler (C:\Windows\System32\tasks).

    :param str xml_text: A string of xml representing the task to be created.
        This will be overridden by `xml_path` if passed.

    :param str xml_path: The path to an XML file on the local system containing
        the xml that defines the task. This will override `xml_text`

    :param str user_name: The user account under which to run the task. To
        specify the 'System' account, use 'System'. The password will be
        ignored.

    :param str password: The password to use for authentication. This should set
        the task to run whether the user is logged in or not, but is currently
        not working.

    :return: True if successful, False if unsuccessful
    :rtype: bool

    CLI Example:

    .. code-block:: bash

        salt 'minion-id' task.create_task_from_xml <task_name> xml_path=C:\task.xml
    '''
    # Check for existing task
    if name in list_tasks(location):
        # Connect to an existing task definition
        return '{0} already exists'.format(name)

    if not xml_text and not xml_path:
        return 'Must specify either xml_text or xml_path'

    # Create the task service object
    pythoncom.CoInitialize()
    task_service = win32com.client.Dispatch("Schedule.Service")
    task_service.Connect()

    # Load xml from file, overrides xml_text
    # Need to figure out how to load contents of xml
    if xml_path:
        xml_text = xml_path

    # Get the folder to list folders from
    task_folder = task_service.GetFolder(location)

    # Determine logon type
    if user_name:
        if user_name.lower() == 'system':
            logon_type = TASK_LOGON_SERVICE_ACCOUNT
            user_name = 'SYSTEM'
            password = None
        else:
            if password:
                logon_type = TASK_LOGON_PASSWORD
            else:
                logon_type = TASK_LOGON_INTERACTIVE_TOKEN
    else:
        password = None

    # Save the task
    try:
        task_folder.RegisterTask(name,
                                 xml_text,
                                 TASK_CREATE,
                                 user_name,
                                 password,
                                 logon_type)

    except pythoncom.com_error as error:
        hr, msg, exc, arg = error.args  # pylint: disable=W0633
        fc = {-2147216615: 'Required element or attribute missing',
              -2147216616: 'Value incorrectly formatted or out of range',
              -2147352571: 'Access denied'}
        try:
            failure_code = fc[exc[5]]
        except KeyError:
            failure_code = 'Unknown Failure: {0}'.format(error)

        log.debug('Failed to create task: {0}'.format(failure_code))

    # Verify creation
    if name in list_tasks(location):
        return True
    else:
        return False