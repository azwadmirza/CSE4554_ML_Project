def add_action(name=None,
               location='\\',
               action_type='Execute',
               **kwargs):
    r'''
    Add an action to a task.

    Args:

        name (str):
            The name of the task to which to add the action.

        location (str):
            A string value representing the location of the task. Default is
            ``\`` which is the root for the task scheduler
            (``C:\Windows\System32\tasks``).

        action_type (str):
            The type of action to add. There are three action types. Each one
            requires its own set of Keyword Arguments (kwargs). Valid values
            are:

                - Execute
                - Email
                - Message

    Required arguments for each action_type:

    **Execute**

        Execute a command or an executable

            cmd (str):
                (required) The command / executable to run.

            arguments (str):
                (optional) Arguments to be passed to the command / executable.
                To launch a script the first command will need to be the
                interpreter for the script. For example, to run a vbscript you
                would pass ``cscript.exe`` in the ``cmd`` parameter and pass the
                script in the ``arguments`` parameter as follows:

                    - ``cmd='cscript.exe' arguments='c:\scripts\myscript.vbs'``

                Batch files do not need an interpreter and may be passed to the
                cmd parameter directly.

            start_in (str):
                (optional) The current working directory for the command.

    **Email**

        Send and email. Requires ``server``, ``from``, and ``to`` or ``cc``.

            from (str): The sender

            reply_to (str): Who to reply to

            to (str): The recipient

            cc (str): The CC recipient

            bcc (str): The BCC recipient

            subject (str): The subject of the email

            body (str): The Message Body of the email

            server (str): The server used to send the email

            attachments (list):
                A list of attachments. These will be the paths to the files to
                attach. ie: ``attachments="['C:\attachment1.txt',
                'C:\attachment2.txt']"``

    **Message**

        Display a dialog box. The task must be set to "Run only when user is
        logged on" in order for the dialog box to display. Both parameters are
        required.

            title (str):
                The dialog box title.

            message (str):
                The dialog box message body

    Returns:
        dict: A dictionary containing the task configuration

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