def runas_system(cmd, username, password, cwd=None):
    # This only works as system, when salt is running as a service for example

    # Check for a domain
    domain = '.'
    if '@' in username:
        username, domain = username.split('@')
    if '\\' in username:
        domain, username = username.split('\\')

    # Load User and Get Token
    token = win32security.LogonUser(username,
                                    domain,
                                    password,
                                    win32con.LOGON32_LOGON_INTERACTIVE,
                                    win32con.LOGON32_PROVIDER_DEFAULT)

    # Load the User Profile
    handle_reg = win32profile.LoadUserProfile(token, {'UserName': username})

    try:
        # Get Unrestricted Token (UAC) if this is an Admin Account
        elevated_token = win32security.GetTokenInformation(
            token, win32security.TokenLinkedToken)

        # Get list of privileges this token contains
        privileges = win32security.GetTokenInformation(
            elevated_token, win32security.TokenPrivileges)

        # Create a set of all privileges to be enabled
        enable_privs = set()
        for luid, flags in privileges:
            enable_privs.add((luid, win32con.SE_PRIVILEGE_ENABLED))

        # Enable the privileges
        win32security.AdjustTokenPrivileges(elevated_token, 0, enable_privs)

    except win32security.error as exc:
        # User doesn't have admin, use existing token
        if exc.winerror == winerror.ERROR_NO_SUCH_LOGON_SESSION \
                or exc.winerror == winerror.ERROR_PRIVILEGE_NOT_HELD:
            elevated_token = token
        else:
            raise

    # Get Security Attributes
    security_attributes = win32security.SECURITY_ATTRIBUTES()
    security_attributes.bInheritHandle = 1

    # Create a pipe to set as stdout in the child. The write handle needs to be
    # inheritable.
    stdin_read, stdin_write = win32pipe.CreatePipe(security_attributes, 0)
    stdin_read = make_inheritable(stdin_read)

    stdout_read, stdout_write = win32pipe.CreatePipe(security_attributes, 0)
    stdout_write = make_inheritable(stdout_write)

    stderr_read, stderr_write = win32pipe.CreatePipe(security_attributes, 0)
    stderr_write = make_inheritable(stderr_write)

    # Get startup info structure
    startup_info = win32process.STARTUPINFO()
    startup_info.dwFlags = win32con.STARTF_USESTDHANDLES
    startup_info.hStdInput = stdin_read
    startup_info.hStdOutput = stdout_write
    startup_info.hStdError = stderr_write

    # Get User Environment
    user_environment = win32profile.CreateEnvironmentBlock(token, False)

    # Build command
    cmd = 'cmd /c {0}'.format(cmd)

    # Run command and return process info structure
    procArgs = (None,
                cmd,
                security_attributes,
                security_attributes,
                1,
                0,
                user_environment,
                cwd,
                startup_info)

    hProcess, hThread, PId, TId = \
        win32process.CreateProcessAsUser(elevated_token, *procArgs)

    if stdin_read is not None:
        stdin_read.Close()
    if stdout_write is not None:
        stdout_write.Close()
    if stderr_write is not None:
        stderr_write.Close()
    hThread.Close()

    # Initialize ret and set first element
    ret = {'pid': PId}

    # Get Standard Out
    fd_out = msvcrt.open_osfhandle(stdout_read, os.O_RDONLY | os.O_TEXT)
    with os.fdopen(fd_out, 'r') as f_out:
        ret['stdout'] = f_out.read()

    # Get Standard Error
    fd_err = msvcrt.open_osfhandle(stderr_read, os.O_RDONLY | os.O_TEXT)
    with os.fdopen(fd_err, 'r') as f_err:
        ret['stderr'] = f_err.read()

    # Get Return Code
    if win32event.WaitForSingleObject(hProcess, win32event.INFINITE) == win32con.WAIT_OBJECT_0:
        exitcode = win32process.GetExitCodeProcess(hProcess)
        ret['retcode'] = exitcode

    # Close handle to process
    win32api.CloseHandle(hProcess)

    # Unload the User Profile
    win32profile.UnloadUserProfile(token, handle_reg)

    return ret