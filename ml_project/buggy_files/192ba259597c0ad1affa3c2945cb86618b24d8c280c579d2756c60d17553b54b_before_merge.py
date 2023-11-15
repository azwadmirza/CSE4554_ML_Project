def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='path', aliases=['dest', 'file']),
            xmlstring=dict(type='str'),
            xpath=dict(type='str', default='/'),
            namespaces=dict(type='dict', default={}),
            state=dict(type='str', default='present', choices=['absent', 'present'], aliases=['ensure']),
            value=dict(),
            attribute=dict(),
            add_children=dict(type='list'),
            set_children=dict(type='list'),
            count=dict(type='bool', default=False),
            print_match=dict(type='bool', default=False),
            pretty_print=dict(type='bool', default=False),
            content=dict(type='str', choices=['attribute', 'text']),
            input_type=dict(type='str', default='yaml', choices=['xml', 'yaml'])
        ),
        supports_check_mode=True,
        mutually_exclusive=[
            ['value', 'set_children'],
            ['value', 'add_children'],
            ['set_children', 'add_children'],
            ['path', 'xmlstring'],
            ['content', 'set_children'],
            ['content', 'add_children'],
            ['content', 'value'],
        ]
    )

    xml_file = module.params['path']
    xml_string = module.params['xmlstring']
    xpath = module.params['xpath']
    namespaces = module.params['namespaces']
    state = module.params['state']
    value = json_dict_bytes_to_unicode(module.params['value'])
    attribute = module.params['attribute']
    set_children = json_dict_bytes_to_unicode(module.params['set_children'])
    add_children = json_dict_bytes_to_unicode(module.params['add_children'])
    pretty_print = module.params['pretty_print']
    content = module.params['content']
    input_type = module.params['input_type']
    print_match = module.params['print_match']
    count = module.params['count']

    # Check if we have lxml 2.3.0 or newer installed
    if not HAS_LXML:
        module.fail_json(msg='The xml ansible module requires the lxml python library installed on the managed machine')
    elif LooseVersion('.'.join(to_native(f) for f in etree.LXML_VERSION)) < LooseVersion('2.3.0'):
        module.fail_json(msg='The xml ansible module requires lxml 2.3.0 or newer installed on the managed machine')
    elif LooseVersion('.'.join(to_native(f) for f in etree.LXML_VERSION)) < LooseVersion('3.0.0'):
        module.warn('Using lxml version lower than 3.0.0 does not guarantee predictable element attribute order.')

    # Check if the file exists
    if xml_string:
        infile = BytesIO(to_bytes(xml_string, errors='surrogate_or_strict'))
    elif os.path.isfile(xml_file):
        infile = open(xml_file, 'rb')
    else:
        module.fail_json(msg="The target XML source '%s' does not exist." % xml_file)

    # Try to parse in the target XML file
    try:
        parser = etree.XMLParser(remove_blank_text=pretty_print)
        doc = etree.parse(infile, parser)
    except etree.XMLSyntaxError as e:
        module.fail_json(msg="Error while parsing path: %s" % e)

    if print_match:
        print_match(module, doc, xpath, namespaces)

    if count:
        count_nodes(module, doc, xpath, namespaces)

    if content == 'attribute':
        get_element_attr(module, doc, xpath, namespaces)
    elif content == 'text':
        get_element_text(module, doc, xpath, namespaces)

    # module.fail_json(msg="OK. Well, etree parsed the xml file...")

    # module.exit_json(what_did={"foo": "bar"}, changed=True)

    # File exists:
    if state == 'absent':
        # - absent: delete xpath target
        delete_xpath_target(module, doc, xpath, namespaces)
        # Exit
    # - present: carry on

    # children && value both set?: should have already aborted by now
    # add_children && set_children both set?: should have already aborted by now

    # set_children set?
    if set_children:
        set_target_children(module, doc, xpath, namespaces, set_children, input_type)

    # add_children set?
    if add_children:
        add_target_children(module, doc, xpath, namespaces, add_children, input_type)

    # No?: Carry on

    # Is the xpath target an attribute selector?
    if value is not None:
        set_target(module, doc, xpath, namespaces, attribute, value)

    # Format the xml only?
    if pretty_print:
        pretty(module, doc)

    ensure_xpath_exists(module, doc, xpath, namespaces)