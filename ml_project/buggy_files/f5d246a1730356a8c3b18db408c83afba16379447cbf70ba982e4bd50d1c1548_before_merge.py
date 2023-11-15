def send_request(module, obj, check_rc=True):
    request = tostring(obj)
    rc, out, err = exec_command(module, request)
    if rc != 0 and check_rc:
        error_root = fromstring(err)
        fake_parent = Element('root')
        fake_parent.append(error_root)

        error_list = fake_parent.findall('.//nc:rpc-error', NS_MAP)
        if not error_list:
            module.fail_json(msg=str(err))

        warnings = []
        for rpc_error in error_list:
            message = rpc_error.find('./nc:error-message', NS_MAP).text
            severity = rpc_error.find('./nc:error-severity', NS_MAP).text

            if severity == 'warning':
                warnings.append(message)
            else:
                module.fail_json(msg=str(err))
        return warnings
    return fromstring(out)