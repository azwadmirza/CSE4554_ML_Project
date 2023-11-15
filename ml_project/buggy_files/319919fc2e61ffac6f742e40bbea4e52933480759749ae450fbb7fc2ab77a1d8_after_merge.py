def doConfigBackUp(module, prompt, answer):
    host = module.params['host']
    server = module.params['serverip']
    username = module.params['serverusername']
    password = module.params['serverpassword']
    protocol = module.params['protocol'].lower()
    rcPath = module.params['rcpath']
    configType = module.params['configType']
    confPath = rcPath + host + '_' + configType + '.txt'

    retVal = ''

    # config backup command happens here
    command = "copy " + configType + " " + protocol + " " + protocol + "://"
    command = command + username + "@" + server + "/" + confPath
    command = command + " vrf management\n"
    cnos.debugOutput(command + "\n")
    # cnos.checkForFirstTimeAccess(module, command, 'yes/no', 'yes')
    cmd = []
    if(protocol == "scp"):
        scp_cmd1 = [{'command': command, 'prompt': 'timeout:', 'answer': '0'}]
        scp_cmd2 = [{'command': '\n', 'prompt': 'Password:',
                     'answer': password}]
        cmd.extend(scp_cmd1)
        cmd.extend(scp_cmd2)
        retVal = retVal + str(cnos.run_cnos_commands(module, cmd))
    elif(protocol == "sftp"):
        sftp_cmd = [{'command': command, 'prompt': 'Password:',
                     'answer': password}]
        cmd.extend(sftp_cmd)
        retVal = retVal + str(cnos.run_cnos_commands(module, cmd))
    elif(protocol == "ftp"):
        ftp_cmd = [{'command': command, 'prompt': 'Password:',
                    'answer': password}]
        cmd.extend(ftp_cmd)
        retVal = retVal + str(cnos.run_cnos_commands(module, cmd))
    elif(protocol == "tftp"):
        command = "copy " + configType + " " + protocol + " " + protocol
        command = command + "://" + server + "/" + confPath
        command = command + " vrf management\n"
        # cnos.debugOutput(command)
        tftp_cmd = [{'command': command, 'prompt': None, 'answer': None}]
        cmd.extend(tftp_cmd)
        retVal = retVal + str(cnos.run_cnos_commands(module, cmd))
    else:
        return "Error-110"

    return retVal