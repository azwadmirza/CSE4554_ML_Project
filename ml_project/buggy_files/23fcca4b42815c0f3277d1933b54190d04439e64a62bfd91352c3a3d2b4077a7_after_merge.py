def add_trigger(name=None,
                location='\\',
                trigger_type=None,
                trigger_enabled=True,
                start_date=None,
                start_time=None,
                end_date=None,
                end_time=None,
                random_delay=None,
                repeat_interval=None,
                repeat_duration=None,
                repeat_stop_at_duration_end=False,
                execution_time_limit=None,
                delay=None,
                **kwargs):
    r'''
    Add a trigger to a Windows Scheduled task

    .. note::

        Arguments are parsed by the YAML loader and are subject to
        yaml's idiosyncrasies. Therefore, time values in some
        formats (``%H:%M:%S`` and ``%H:%M``) should to be quoted.
        See `YAML IDIOSYNCRASIES`_ for more details.

    .. _`YAML IDIOSYNCRASIES`: https://docs.saltstack.com/en/latest/topics/troubleshooting/yaml_idiosyncrasies.html#time-expressions

    Args:

        name (str):
            The name of the task to which to add the trigger.

        location (str):
            A string value representing the location of the task. Default is
            ``\`` which is the root for the task scheduler
            (``C:\Windows\System32\tasks``).

        trigger_type (str):
            The type of trigger to create. This is defined when the trigger is
            created and cannot be changed later. Options are as follows:

                - Event
                - Once
                - Daily
                - Weekly
                - Monthly
                - MonthlyDay
                - OnIdle
                - OnTaskCreation
                - OnBoot
                - OnLogon
                - OnSessionChange

        trigger_enabled (bool):
            Boolean value that indicates whether the trigger is enabled.

        start_date (str):
            The date when the trigger is activated. If no value is passed, the
            current date will be used. Can be one of the following formats:

                - %Y-%m-%d
                - %m-%d-%y
                - %m-%d-%Y
                - %m/%d/%y
                - %m/%d/%Y
                - %Y/%m/%d

        start_time (str):
            The time when the trigger is activated. If no value is passed,
            midnight will be used. Can be one of the following formats:

                - %I:%M:%S %p
                - %I:%M %p
                - %H:%M:%S
                - %H:%M

        end_date (str):
            The date when the trigger is deactivated. The trigger cannot start
            the task after it is deactivated. Can be one of the following
            formats:

                - %Y-%m-%d
                - %m-%d-%y
                - %m-%d-%Y
                - %m/%d/%y
                - %m/%d/%Y
                - %Y/%m/%d

        end_time (str):
            The time when the trigger is deactivated. If the this is not passed
            with ``end_date`` it will be set to midnight. Can be one of the
            following formats:

                - %I:%M:%S %p
                - %I:%M %p
                - %H:%M:%S
                - %H:%M

        random_delay (str):
            The delay time that is randomly added to the start time of the
            trigger. Valid values are:

                - 30 seconds
                - 1 minute
                - 30 minutes
                - 1 hour
                - 8 hours
                - 1 day

            .. note::

                This parameter applies to the following trigger types

                    - Once
                    - Daily
                    - Weekly
                    - Monthly
                    - MonthlyDay

        repeat_interval (str):
            The amount of time between each restart of the task. Valid values
            are:

                - 5 minutes
                - 10 minutes
                - 15 minutes
                - 30 minutes
                - 1 hour

        repeat_duration (str):
            How long the pattern is repeated. Valid values are:

                - Indefinitely
                - 15 minutes
                - 30 minutes
                - 1 hour
                - 12 hours
                - 1 day

        repeat_stop_at_duration_end (bool):
            Boolean value that indicates if a running instance of the task is
            stopped at the end of the repetition pattern duration.

        execution_time_limit (str):
            The maximum amount of time that the task launched by the trigger is
            allowed to run. Valid values are:

                - 30 minutes
                - 1 hour
                - 2 hours
                - 4 hours
                - 8 hours
                - 12 hours
                - 1 day
                - 3 days (default)

        delay (str):
            The time the trigger waits after its activation to start the task.
            Valid values are:

                - 15 seconds
                - 30 seconds
                - 1 minute
                - 30 minutes
                - 1 hour
                - 8 hours
                - 1 day

            .. note::

                This parameter applies to the following trigger types:

                    - OnLogon
                    - OnBoot
                    - Event
                    - OnTaskCreation
                    - OnSessionChange

    **kwargs**

    There are optional keyword arguments determined by the type of trigger
    being defined. They are as follows:

    *Event*

        The trigger will be fired by an event.

            subscription (str):
                An event definition in xml format that fires the trigger. The
                easiest way to get this would is to create an event in Windows
                Task Scheduler and then copy the xml text.

    *Once*

        No special parameters required.

    *Daily*

        The task will run daily.

            days_interval (int):
                The interval between days in the schedule. An interval of 1
                produces a daily schedule. An interval of 2 produces an
                every-other day schedule. If no interval is specified, 1 is
                used. Valid entries are 1 - 999.

    *Weekly*

        The task will run weekly.

            weeks_interval (int):
                The interval between weeks in the schedule. An interval of 1
                produces a weekly schedule. An interval of 2 produces an
                every-other week schedule. If no interval is specified, 1 is
                used. Valid entries are 1 - 52.

            days_of_week (list):
                Sets the days of the week on which the task runs. Should be a
                list. ie: ``['Monday','Wednesday','Friday']``. Valid entries are
                the names of the days of the week.

    *Monthly*

        The task will run monthly.

            months_of_year (list):
                Sets the months of the year during which the task runs. Should
                be a list. ie: ``['January','July']``. Valid entries are the
                full names of all the months.

            days_of_month (list):
                Sets the days of the month during which the task runs. Should be
                a list. ie: ``[1, 15, 'Last']``. Options are all days of the
                month 1 - 31 and the word 'Last' to indicate the last day of the
                month.

            last_day_of_month (bool):
                Boolean value that indicates that the task runs on the last day
                of the month regardless of the actual date of that day.

                .. note::

                    You can set the task to run on the last day of the month by
                    either including the word 'Last' in the list of days, or
                    setting the parameter 'last_day_of_month' equal to True.

    *MonthlyDay*

        The task will run monthly on the specified day.

            months_of_year (list):
                Sets the months of the year during which the task runs. Should
                be a list. ie: ``['January','July']``. Valid entries are the
                full names of all the months.

            weeks_of_month (list):
                Sets the weeks of the month during which the task runs. Should
                be a list. ie: ``['First','Third']``. Valid options are:

                    - First
                    - Second
                    - Third
                    - Fourth

            last_week_of_month (bool):
                Boolean value that indicates that the task runs on the last week
                of the month.

            days_of_week (list):
                Sets the days of the week during which the task runs. Should be
                a list. ie: ``['Monday','Wednesday','Friday']``.  Valid entries
                are the names of the days of the week.

    *OnIdle*

        No special parameters required.

    *OnTaskCreation*

        No special parameters required.

    *OnBoot*

        No special parameters required.

    *OnLogon*

        No special parameters required.

    *OnSessionChange*

        The task will be triggered by a session change.

            session_user_name (str):
                Sets the user for the Terminal Server session. When a session
                state change is detected for this user, a task is started. To
                detect session status change for any user, do not pass this
                parameter.

            state_change (str):
                Sets the kind of Terminal Server session change that would
                trigger a task launch. Valid options are:

                    - ConsoleConnect: When you connect to a user session (switch
                      users)
                    - ConsoleDisconnect: When you disconnect a user session
                      (switch users)
                    - RemoteConnect: When a user connects via Remote Desktop
                    - RemoteDisconnect: When a user disconnects via Remote
                      Desktop
                    - SessionLock: When the workstation is locked
                    - SessionUnlock: When the workstation is unlocked

    Returns:
        bool: ``True`` if successful, otherwise ``False``

    CLI Example:

    .. code-block:: bash

        salt 'minion-id' task.add_trigger <task_name> trigger_type=Once trigger_enabled=True start_date=2016/12/1 start_time='"12:01"'
    '''
    if not trigger_type:
        return 'Required parameter "trigger_type" not specified'

    # Define lookup dictionaries
    state_changes = {'ConsoleConnect': 1,
                     'ConsoleDisconnect': 2,
                     'RemoteConnect': 3,
                     'RemoteDisconnect': 4,
                     'SessionLock': 7,
                     'SessionUnlock': 8}

    days = {1: 0x1,
            2: 0x2,
            3: 0x4,
            4: 0x8,
            5: 0x10,
            6: 0x20,
            7: 0x40,
            8: 0x80,
            9: 0x100,
            10: 0x200,
            11: 0x400,
            12: 0x800,
            13: 0x1000,
            14: 0x2000,
            15: 0x4000,
            16: 0x8000,
            17: 0x10000,
            18: 0x20000,
            19: 0x40000,
            20: 0x80000,
            21: 0x100000,
            22: 0x200000,
            23: 0x400000,
            24: 0x800000,
            25: 0x1000000,
            26: 0x2000000,
            27: 0x4000000,
            28: 0x8000000,
            29: 0x10000000,
            30: 0x20000000,
            31: 0x40000000,
            'Last': 0x80000000}

    weekdays = {'Sunday': 0x1,
                'Monday': 0x2,
                'Tuesday': 0x4,
                'Wednesday': 0x8,
                'Thursday': 0x10,
                'Friday': 0x20,
                'Saturday': 0x40}

    weeks = {'First': 0x1,
             'Second': 0x2,
             'Third': 0x4,
             'Fourth': 0x8}

    months = {'January': 0x1,
              'February': 0x2,
              'March': 0x4,
              'April': 0x8,
              'May': 0x10,
              'June': 0x20,
              'July': 0x40,
              'August': 0x80,
              'September': 0x100,
              'October': 0x200,
              'November': 0x400,
              'December': 0x800}

    # Format Date Parameters
    if start_date:
        date_format = _get_date_time_format(start_date)
        if date_format:
            dt_obj = datetime.strptime(start_date, date_format)
        else:
            return 'Invalid start_date'
    else:
        dt_obj = datetime.now()

    if start_time:
        time_format = _get_date_time_format(start_time)
        if time_format:
            tm_obj = datetime.strptime(start_time, time_format)
        else:
            return 'Invalid start_time'
    else:
        tm_obj = datetime.strptime('00:00:00', '%H:%M:%S')

    start_boundary = '{0}T{1}'.format(dt_obj.strftime('%Y-%m-%d'),
                                      tm_obj.strftime('%H:%M:%S'))

    dt_obj = None
    if end_date:
        date_format = _get_date_time_format(end_date)
        if date_format:
            dt_obj = datetime.strptime(end_date, date_format)
        else:
            return 'Invalid end_date'

    if end_time:
        time_format = _get_date_time_format(end_time)
        if time_format:
            tm_obj = datetime.strptime(end_time, time_format)
        else:
            return 'Invalid end_time'
    else:
        tm_obj = datetime.strptime('00:00:00', '%H:%M:%S')

    end_boundary = None
    if dt_obj and tm_obj:
        end_boundary = '{0}T{1}'.format(dt_obj.strftime('%Y-%m-%d'),
                                        tm_obj.strftime('%H:%M:%S'))

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

    # Create a New Trigger
    trigger = task_definition.Triggers.Create(trigger_types[trigger_type])

    # Shared Trigger Parameters
    # Settings
    trigger.StartBoundary = start_boundary
    # Advanced Settings
    if delay:
        trigger.Delay = _lookup_first(duration, delay)
    if random_delay:
        trigger.RandomDelay = _lookup_first(duration, random_delay)
    if repeat_interval:
        trigger.Repetition.Interval = _lookup_first(duration, repeat_interval)
        if repeat_duration:
            trigger.Repetition.Duration = _lookup_first(duration,
                                                        repeat_duration)
        trigger.Repetition.StopAtDurationEnd = repeat_stop_at_duration_end
    if execution_time_limit:
        trigger.ExecutionTimeLimit = _lookup_first(duration,
                                                   execution_time_limit)
    if end_boundary:
        trigger.EndBoundary = end_boundary
    trigger.Enabled = trigger_enabled

    # Trigger Specific Parameters
    # Event Trigger Parameters
    if trigger_types[trigger_type] == TASK_TRIGGER_EVENT:
        # Check for required kwargs
        if kwargs.get('subscription', False):
            trigger.Id = 'Event_ID1'
            trigger.Subscription = kwargs.get('subscription')
        else:
            return 'Required parameter "subscription" not passed'

    elif trigger_types[trigger_type] == TASK_TRIGGER_TIME:
        trigger.Id = 'Once_ID1'

    # Daily Trigger Parameters
    elif trigger_types[trigger_type] == TASK_TRIGGER_DAILY:
        trigger.Id = 'Daily_ID1'
        trigger.DaysInterval = kwargs.get('days_interval', 1)

    # Weekly Trigger Parameters
    elif trigger_types[trigger_type] == TASK_TRIGGER_WEEKLY:
        trigger.Id = 'Weekly_ID1'
        trigger.WeeksInterval = kwargs.get('weeks_interval', 1)
        if kwargs.get('days_of_week', False):
            bits_days = 0
            for weekday in kwargs.get('days_of_week'):
                bits_days |= weekdays[weekday]
            trigger.DaysOfWeek = bits_days
        else:
            return 'Required parameter "days_of_week" not passed'

    # Monthly Trigger Parameters
    elif trigger_types[trigger_type] == TASK_TRIGGER_MONTHLY:
        trigger.Id = 'Monthly_ID1'
        if kwargs.get('months_of_year', False):
            bits_months = 0
            for month in kwargs.get('months_of_year'):
                bits_months |= months[month]
            trigger.MonthsOfYear = bits_months
        else:
            return 'Required parameter "months_of_year" not passed'

        if kwargs.get('days_of_month', False) or \
                kwargs.get('last_day_of_month', False):
            if kwargs.get('days_of_month', False):
                bits_days = 0
                for day in kwargs.get('days_of_month'):
                    bits_days |= days[day]
                trigger.DaysOfMonth = bits_days
            trigger.RunOnLastDayOfMonth = kwargs.get('last_day_of_month', False)
        else:
            return 'Monthly trigger requires "days_of_month" or "last_day_of_' \
                   'month" parameters'

    # Monthly Day Of Week Trigger Parameters
    elif trigger_types[trigger_type] == TASK_TRIGGER_MONTHLYDOW:
        trigger.Id = 'Monthly_DOW_ID1'
        if kwargs.get('months_of_year', False):
            bits_months = 0
            for month in kwargs.get('months_of_year'):
                bits_months |= months[month]
            trigger.MonthsOfYear = bits_months
        else:
            return 'Required parameter "months_of_year" not passed'

        if kwargs.get('weeks_of_month', False) or \
                kwargs.get('last_week_of_month', False):
            if kwargs.get('weeks_of_month', False):
                bits_weeks = 0
                for week in kwargs.get('weeks_of_month'):
                    bits_weeks |= weeks[week]
                trigger.WeeksOfMonth = bits_weeks
            trigger.RunOnLastWeekOfMonth = kwargs.get('last_week_of_month',
                                                      False)
        else:
            return 'Monthly DOW trigger requires "weeks_of_month" or "last_' \
                   'week_of_month" parameters'

        if kwargs.get('days_of_week', False):
            bits_days = 0
            for weekday in kwargs.get('days_of_week'):
                bits_days |= weekdays[weekday]
            trigger.DaysOfWeek = bits_days
        else:
            return 'Required parameter "days_of_week" not passed'

    # On Idle Trigger Parameters
    elif trigger_types[trigger_type] == TASK_TRIGGER_IDLE:
        trigger.Id = 'OnIdle_ID1'

    # On Task Creation Trigger Parameters
    elif trigger_types[trigger_type] == TASK_TRIGGER_REGISTRATION:
        trigger.Id = 'OnTaskCreation_ID1'

    # On Boot Trigger Parameters
    elif trigger_types[trigger_type] == TASK_TRIGGER_BOOT:
        trigger.Id = 'OnBoot_ID1'

    # On Logon Trigger Parameters
    elif trigger_types[trigger_type] == TASK_TRIGGER_LOGON:
        trigger.Id = 'OnLogon_ID1'

    # On Session State Change Trigger Parameters
    elif trigger_types[trigger_type] == TASK_TRIGGER_SESSION_STATE_CHANGE:
        trigger.Id = 'OnSessionStateChange_ID1'
        if kwargs.get('session_user_name', False):
            trigger.UserId = kwargs.get('session_user_name')
        if kwargs.get('state_change', False):
            trigger.StateChange = state_changes[kwargs.get('state_change')]
        else:
            return 'Required parameter "state_change" not passed'

    # Save the task
    if save_definition:
        # Save the Changes
        return _save_task_definition(name=name,
                                     task_folder=task_folder,
                                     task_definition=task_definition,
                                     user_name=task_definition.Principal.UserID,
                                     password=None,
                                     logon_type=task_definition.Principal.LogonType)