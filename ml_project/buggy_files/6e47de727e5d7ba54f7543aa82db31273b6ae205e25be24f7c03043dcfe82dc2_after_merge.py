def build_xml(container, xmap=None, params=None, opcode=None):
    """
    Builds netconf xml rpc document from meta-data

    Args:
        container: the YANG container within the namespace
        xmap: meta-data map to build xml tree
        params: Input params that feed xml tree values
        opcode: operation to be performed (merge, delete etc.)

    Example:
        Module inputs:
            banner_params = [{'banner':'motd', 'text':'Ansible banner example', 'state':'present'}]

        Meta-data definition:
            bannermap = collections.OrderedDict()
            bannermap.update([
                ('banner', {'xpath' : 'banners/banner', 'tag' : True, 'attrib' : "operation"}),
                ('a:banner', {'xpath' : 'banner/banner-name'}),
                ('a:text', {'xpath' : 'banner/banner-text', 'operation' : 'edit'})
            ])

            Fields:
                key: exact match to the key in arg_spec for a parameter
                   (prefixes --> a: value fetched from arg_spec, m: value fetched from meta-data)
                xpath: xpath of the element (based on YANG model)
                tag: True if no text on the element
                attrib: attribute to be embedded in the element (e.g. xc:operation="merge")
                operation: if edit --> includes the element in edit_config() query else ignores for get() queries
                value: if key is prefixed with "m:", value is required in meta-data

        Output:
            <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
              <banners xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-infra-infra-cfg">
                <banner xc:operation="merge">
                  <banner-name>motd</banner-name>
                  <banner-text>Ansible banner example</banner-text>
                </banner>
              </banners>
            </config>
    :returns: xml rpc document as a string
    """
    if opcode == 'filter':
        root = etree.Element("filter", type="subtree")
    elif opcode in ('delete', 'merge'):
        root = etree.Element("config", nsmap=NS_DICT['BASE_NSMAP'])

    container_ele = etree.SubElement(root, container, nsmap=NS_DICT[container.upper() + "_NSMAP"])

    if xmap is not None:
        if params is None:
            build_xml_subtree(container_ele, xmap, opcode=opcode)
        else:
            subtree_list = list()
            for param in to_list(params):
                subtree_ele = build_xml_subtree(container_ele, xmap, param=param, opcode=opcode)
                if subtree_ele is not None:
                    subtree_list.append(subtree_ele)

            for item in subtree_list:
                container_ele.append(item)

    return etree.tostring(root, encoding='unicode')