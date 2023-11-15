def delete_office_registrymodifications(path):
    """Erase LibreOffice 3.4 and Apache OpenOffice.org 3.4 MRU in registrymodifications.xcu"""
    import xml.dom.minidom
    dom1 = xml.dom.minidom.parse(path)
    modified = False
    for node in dom1.getElementsByTagName("item"):
        if not node.hasAttribute("oor:path"):
            continue
        if not node.getAttribute("oor:path").startswith('/org.openoffice.Office.Histories/Histories/'):
            continue
        node.parentNode.removeChild(node)
        node.unlink()
        modified = True
    if modified:
        with open(path, 'w', encoding='utf-8') as xml_file:
            dom1.writexml(xml_file)