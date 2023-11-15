def delete_ooo_history(path):
    """Erase the OpenOffice.org MRU in Common.xcu.  No longer valid in Apache OpenOffice.org 3.4."""
    import xml.dom.minidom
    dom1 = xml.dom.minidom.parse(path)
    changed = False
    for node in dom1.getElementsByTagName("node"):
        if node.hasAttribute("oor:name"):
            if "History" == node.getAttribute("oor:name"):
                node.parentNode.removeChild(node)
                node.unlink()
                changed = True
                break
    if changed:
        dom1.writexml(open(path, "w", encoding='utf-8'))