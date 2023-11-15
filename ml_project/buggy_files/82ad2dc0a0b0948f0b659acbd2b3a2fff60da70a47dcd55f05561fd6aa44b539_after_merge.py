def _write_regpol_data(data_to_write,
                       policy_file_path,
                       gpt_ini_path,
                       gpt_extension,
                       gpt_extension_guid):
    '''
    helper function to actually write the data to a Registry.pol file

    also updates/edits the gpt.ini file to include the ADM policy extensions
    to let the computer know user and/or machine registry policy files need
    to be processed

    data_to_write: data to write into the user/machine registry.pol file
    policy_file_path: path to the registry.pol file
    gpt_ini_path: path to gpt.ini file
    gpt_extension: gpt extension list name from _policy_info class for this registry class gpt_extension_location
    gpt_extension_guid: admx registry extension guid for the class
    '''
    try:
        reg_pol_header = u'\u5250\u6765\x01\x00'
        if not os.path.exists(policy_file_path):
            ret = __salt__['file.makedirs'](policy_file_path)
        with salt.utils.fopen(policy_file_path, 'wb') as pol_file:
            if not data_to_write.startswith(reg_pol_header.encode('utf-16-le')):
                pol_file.write(reg_pol_header.encode('utf-16-le'))
            pol_file.write(data_to_write)
        try:
            gpt_ini_data = ''
            if os.path.exists(gpt_ini_path):
                with salt.utils.fopen(gpt_ini_path, 'rb') as gpt_file:
                    gpt_ini_data = gpt_file.read()
            if not _regexSearchRegPolData(r'\[General\]\r\n', gpt_ini_data):
                gpt_ini_data = '[General]\r\n' + gpt_ini_data
            if _regexSearchRegPolData(r'{0}='.format(re.escape(gpt_extension)), gpt_ini_data):
                # ensure the line contains the ADM guid
                gpt_ext_loc = re.search(r'^{0}=.*\r\n'.format(re.escape(gpt_extension)),
                                        gpt_ini_data,
                                        re.IGNORECASE | re.MULTILINE)
                gpt_ext_str = gpt_ini_data[gpt_ext_loc.start():gpt_ext_loc.end()]
                if not _regexSearchRegPolData(r'{0}'.format(re.escape(gpt_extension_guid)),
                                              gpt_ext_str):
                    gpt_ext_str = gpt_ext_str.split('=')
                    gpt_ext_str[1] = gpt_extension_guid + gpt_ext_str[1]
                    gpt_ext_str = '='.join(gpt_ext_str)
                    gpt_ini_data = gpt_ini_data[0:gpt_ext_loc.start()] + gpt_ext_str + gpt_ini_data[gpt_ext_loc.end():]
            else:
                general_location = re.search(r'^\[General\]\r\n',
                                             gpt_ini_data,
                                             re.IGNORECASE | re.MULTILINE)
                gpt_ini_data = "{0}{1}={2}\r\n{3}".format(
                        gpt_ini_data[general_location.start():general_location.end()],
                        gpt_extension, gpt_extension_guid,
                        gpt_ini_data[general_location.end():])
            # https://technet.microsoft.com/en-us/library/cc978247.aspx
            if _regexSearchRegPolData(r'Version=', gpt_ini_data):
                version_loc = re.search(r'^Version=.*\r\n',
                                        gpt_ini_data,
                                        re.IGNORECASE | re.MULTILINE)
                version_str = gpt_ini_data[version_loc.start():version_loc.end()]
                version_str = version_str.split('=')
                version_nums = struct.unpack('>2H', struct.pack('>I', int(version_str[1])))
                if gpt_extension.lower() == 'gPCMachineExtensionNames'.lower():
                    version_nums = (version_nums[0], version_nums[1] + 1)
                elif gpt_extension.lower() == 'gPCUserExtensionNames'.lower():
                    version_nums = (version_nums[0] + 1, version_nums[1])
                version_num = struct.unpack('>I', struct.pack('>2H', *version_nums))[0]
                gpt_ini_data = "{0}{1}={2}\r\n{3}".format(
                        gpt_ini_data[0:version_loc.start()],
                        'Version', version_num,
                        gpt_ini_data[version_loc.end():])
            else:
                general_location = re.search(r'^\[General\]\r\n',
                                             gpt_ini_data,
                                             re.IGNORECASE | re.MULTILINE)
                if gpt_extension.lower() == 'gPCMachineExtensionNames'.lower():
                    version_nums = (0, 1)
                elif gpt_extension.lower() == 'gPCUserExtensionNames'.lower():
                    version_nums = (1, 0)
                gpt_ini_data = "{0}{1}={2}\r\n{3}".format(
                        gpt_ini_data[general_location.start():general_location.end()],
                        'Version',
                        int("{0}{1}".format(str(version_nums[0]).zfill(4), str(version_nums[1]).zfill(4)), 16),
                        gpt_ini_data[general_location.end():])
            if gpt_ini_data:
                with salt.utils.fopen(gpt_ini_path, 'wb') as gpt_file:
                    gpt_file.write(gpt_ini_data)
        except Exception as e:
            msg = 'An error occurred attempting to write to {0}, the exception was {1}'.format(
                    gpt_ini_path, e)
            raise CommandExecutionError(msg)
    except Exception as e:
        msg = 'An error occurred attempting to write to {0}, the exception was {1}'.format(policy_file_path, e)
        raise CommandExecutionError(msg)