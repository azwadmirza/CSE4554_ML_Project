def rpc(module, items):

    responses = list()

    for item in items:
        name = item['name']
        xattrs = item['xattrs']

        args = item.get('args')
        text = item.get('text')

        name = str(name).replace('_', '-')

        if all((module.check_mode, not name.startswith('get'))):
            module.fail_json(msg='invalid rpc for running in check_mode')

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

        reply = send_request(module, element)

        if xattrs['format'] == 'text':
            data = reply.find('.//output')
            responses.append(data.text.strip())

        elif xattrs['format'] == 'json':
            responses.append(module.from_json(reply.text.strip()))

        else:
            responses.append(tostring(reply))

    return responses