def doImageDownload(module, prompt, answer):
    protocol = module.params['protocol'].lower()
    server = module.params['serverip']
    imgPath = module.params['imgpath']
    imgType = module.params['imgtype']
    username = module.params['serverusername']
    password = module.params['serverpassword']
    retVal = ''
    command = "copy " + protocol + " " + protocol + "://" + username + "@"
    command = command + server + "/" + imgPath + " system-image "
    command = command + imgType + " vrf management"
    cmd = []
    if(protocol == "scp"):
        prompt = ['timeout', 'Confirm download operation', 'Password',
                  'Do you want to change that to the standby image']
        answer = ['240', 'y', password, 'y']
        scp_cmd = [{'command': command, 'prompt': prompt, 'answer': answer,
                    'check_all': True}]
        cmd.extend(scp_cmd)
        retVal = retVal + str(cnos.run_cnos_commands(module, cmd))
    elif(protocol == "sftp"):
        prompt = ['Confirm download operation', 'Password',
                  'Do you want to change that to the standby image']
        answer = ['y', password, 'y']
        sftp_cmd = [{'command': command, 'prompt': prompt, 'answer': answer,
                     'check_all': True}]
        cmd.extend(sftp_cmd)
        retVal = retVal + str(cnos.run_cnos_commands(module, cmd))
    elif(protocol == "ftp"):
        prompt = ['Confirm download operation', 'Password',
                  'Do you want to change that to the standby image']
        answer = ['y', password, 'y']
        ftp_cmd = [{'command': command, 'prompt': prompt, 'answer': answer,
                    'check_all': True}]
        cmd.extend(ftp_cmd)
        retVal = retVal + str(cnos.run_cnos_commands(module, cmd))
    elif(protocol == "tftp"):
        command = "copy " + protocol + " " + protocol + "://" + server
        command = command + "/" + imgPath + " system-image " + imgType
        command = command + " vrf management"
        prompt = ['Confirm download operation',
                  'Do you want to change that to the standby image']
        answer = ['y', 'y']
        tftp_cmd = [{'command': command, 'prompt': prompt, 'answer': answer,
                     'check_all': True}]
        cmd.extend(tftp_cmd)
        retVal = retVal + str(cnos.run_cnos_commands(module, cmd))
    else:
        return "Error-110"

    return retVal