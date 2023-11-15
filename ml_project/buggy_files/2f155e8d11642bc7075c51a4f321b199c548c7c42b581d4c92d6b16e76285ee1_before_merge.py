def add_action(name=None,
               location='\\',
               action_type='Execute',
               **kwargs):
    r'''
    Add an action to a task.

    :param str name: The name of the task to which to add the action.

    :param str location: A string value representing the location of the task.
        Default is '\\' which is the root for the task scheduler
        (C:\Windows\System32\tasks).

    :param str action_type: The type of action to add. There are three action
        types. Each one requires its own set of Keyword Arguments (kwargs). Valid
        values are:

        - Execute
        - Email
        - Message

    Required arguments for each action_type:

    **Execute** - Execute a command or an executable

    :param str cmd: (required) The command / executable to run.

    :param str arguments: (optional) Arguments to be passed to the command /
        executable. To launch a script the first command will need to be the
        interpreter for the script. For example, to run a vbscript you would
        pass `cscript.exe` in the `cmd` parameter and pass the script in the
        `arguments` parameter as follows:

        - ``cmd='cscript.exe' arguments='c:\scripts\myscript.vbs'``

        Batch files do not need an interpreter and may be passed to the cmd
        parameter directly.

    :param str start_in: (optional) The current working directory for the
        command.

    **Email** - Send and email. Requires ``server``, ``from``, and ``to`` or
    ``cc``.

    :param str from: The sender
    :param str reply_to: Who to reply to
    :param str to: The recipient
    :param str cc: The CC recipient
    :param str bcc: The BCC recipient
    :param str subject: The subject of the email
    :param str body: The Message Body of the email
    :param str server: The server used to send the email
    :param list attachments: A list of attachments. These will be the paths to
        the files to attach. ie: ``attachments="['C:\attachment1.txt',
        'C:\attachment2.txt']"``

    **Message** - Display a dialog box. The task must be set to "Run only when
    user is logged on" in order for the dialog box to display. Both parameters
    are required.

    :param str title: The dialog box title.
    :param str message: The dialog box message body

    :return: True if successful, False if unsuccessful
    :rtype: bool

    CLI Example:

    .. code-block:: bash

        salt 'minion-id' task.add_action <task_name> cmd='del /Q /S C:\\Temp'
    '''
    save_definition = False
    if kwargs.get('task_definition', False):
        task_definition = kwargs.get('task_definition')
    else:
        save_definition = True
        # Make sure a name was passed
        if not name:
            return 'Required parameter "name" not passed'

        # Make sure task exists
        if name in list_tasks(location):

            # Connect to the task scheduler
            pythoncom.CoInitialize()
            task_service = win32com.client.Dispatch("Schedule.Service")
            task_service.Connect()

            # get the folder to create the task in
            task_folder = task_service.GetFolder(location)

            # Connect to an existing task definition
            task_definition = task_folder.GetTask(name).Definition

        else:
            # Not found and create_new not set, return not found
            return '{0} not found'.format(name)

    # Action Settings
    task_action = task_definition.Actions.Create(action_types[action_type])
    if action_types[action_type] == TASK_ACTION_EXEC:
        task_action.Id = 'Execute_ID1'
        if kwargs.get('cmd', False):
            task_action.Path = kwargs.get('cmd')
        else:
            return 'Required parameter "cmd" not found'
        task_action.Arguments = kwargs.get('arguments', '')
        task_action.WorkingDirectory = kwargs.get('start_in', '')

    elif action_types[action_type] == TASK_ACTION_SEND_EMAIL:
        task_action.Id = 'Email_ID1'

        # Required Parameters
        if kwargs.get('server', False):
            task_action.Server = kwargs.get('server')
        else:
            return 'Required parameter "server" not found'

        if kwargs.get('from', False):
            task_action.From = kwargs.get('from')
        else:
            return 'Required parameter "from" not found'

        if kwargs.get('to', False) or kwargs.get('cc', False):
            if kwargs.get('to'):
                task_action.To = kwargs.get('to')
            if kwargs.get('cc'):
                task_action.Cc = kwargs.get('cc')
        else:
            return 'Required parameter "to" or "cc" not found'

        # Optional Parameters
        if kwargs.get('reply_to'):
            task_action.ReplyTo = kwargs.get('reply_to')
        if kwargs.get('bcc'):
            task_action.Bcc = kwargs.get('bcc')
        if kwargs.get('subject'):
            task_action.Subject = kwargs.get('subject')
        if kwargs.get('body'):
            task_action.Body = kwargs.get('body')
        if kwargs.get('attachments'):
            task_action.Attachments = kwargs.get('attachments')

    elif action_types[action_type] == TASK_ACTION_SHOW_MESSAGE:
        task_action.Id = 'Message_ID1'

        if kwargs.get('title', False):
            task_action.Title = kwargs.get('title')
        else:
            return 'Required parameter "title" not found'

        if kwargs.get('message', False):
            task_action.MessageBody = kwargs.get('message')
        else:
            return 'Required parameter "message" not found'

    # Save the task
    if save_definition:
        # Save the Changes
        return _save_task_definition(name=name,
                                     task_folder=task_folder,
                                     task_definition=task_definition,
                                     user_name=task_definition.Principal.UserID,
                                     password=None,
                                     logon_type=task_definition.Principal.LogonType)