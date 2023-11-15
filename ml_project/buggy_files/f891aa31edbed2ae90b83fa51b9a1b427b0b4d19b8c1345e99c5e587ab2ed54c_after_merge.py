def rpc(module, items):

    responses = list()

    for item in items:
        name = item['name']
        xattrs = item['xattrs']
        fetch_config = False

        args = item.get('args')
        text = item.get('text')

        name = str(name).replace('_', '-')

        if all((module.check_mode, not name.startswith('get'))):
            module.fail_json(msg='invalid rpc for running in check_mode')

        if name == 'command' and text.startswith('show configuration') or name == 'get-configuration':
            fetch_config = True

        element = Element(name, xattrs)

        if text:
            element.text = text

        elif args:
            for key, value in iteritems(args):
                key = str(key).replace('_', '-')
                if isinstance(value, list):
                    for item in value:
                        child = SubElement(element, key)
                        if item is not True:
                            child.text = item
                else:
                    child = SubElement(element, key)
                    if value is not True:
                        child.text = value

        if fetch_config:
            reply = get_configuration(module, format=xattrs['format'])
        else:
            reply = send_request(module, element, ignore_warning=False)

        if xattrs['format'] == 'text':
            if fetch_config:
                data = reply.find('.//configuration-text')
            else:
                data = reply.find('.//output')

            if data is None:
                module.fail_json(msg=tostring(reply))

            responses.append(data.text.strip())

        elif xattrs['format'] == 'json':
            responses.append(module.from_json(reply.text.strip()))

        elif xattrs['format'] == 'set':
            data = reply.find('.//configuration-set')
            if data is None:
                module.fail_json(msg="Display format 'set' is not supported by remote device.")
            responses.append(data.text.strip())

        else:
            responses.append(tostring(reply))

    return responses