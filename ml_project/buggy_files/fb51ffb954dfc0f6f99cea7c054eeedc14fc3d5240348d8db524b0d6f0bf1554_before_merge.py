def _parse_xml(app_dir):
    """Parse the AppxManifest file to get basic informations."""
    logger.info("Starting Binary Analysis - XML")
    xml_file = os.path.join(app_dir, "AppxManifest.xml")
    xml_dic = {
        'version': '',
        'arch': '',
        'app_name': '',
        'pub_name': '',
        'compiler_version': '',
        'visual_studio_version': '',
        'visual_studio_edition': '',
        'target_os': '',
        'appx_dll_version': '',
        'proj_guid': '',
        'opti_tool': '',
        'target_run': ''
    }

    try:
        logger.info("Reading AppxManifest")
        config = etree.XMLParser(  # pylint: disable-msg=E1101
            remove_blank_text=True,
            resolve_entities=False
        )
        xml = etree.XML(open(xml_file, "rb").read(),
                        config)  # pylint: disable-msg=E1101
        for child in xml.getchildren():
            # } to prevent conflict with PhoneIdentity..
            if isinstance(child.tag, str) and child.tag.endswith("}Identity"):
                xml_dic['version'] = child.get("Version")
                xml_dic['arch'] = child.get("ProcessorArchitecture")
            elif isinstance(child.tag, str) and child.tag.endswith("Properties"):
                for sub_child in child.getchildren():
                    if sub_child.tag.endswith("}DisplayName"):
                        # TODO(Needed? Compare to existing app_name)
                        xml_dic['app_name'] = sub_child.text
                    elif sub_child.tag.endswith("}PublisherDisplayName"):
                        xml_dic['pub_name'] = sub_child.text
            elif isinstance(child.tag, str) and child.tag.endswith("}Metadata"):
                xml_dic = __parse_xml_metadata(xml_dic, child)
    except:
        PrintException("[ERROR] - Reading from AppxManifest.xml")
    return xml_dic