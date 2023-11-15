def get_vtp_password(module):
    command = 'show vtp password'
    body = execute_show_command(command, module)[0]
    try:
        password = body['passwd']
        if password:
            return str(password)
        else:
            return ""
    except TypeError:
        return ""