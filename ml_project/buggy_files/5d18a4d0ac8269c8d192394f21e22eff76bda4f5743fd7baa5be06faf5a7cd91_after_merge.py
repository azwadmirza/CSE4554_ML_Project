def parse_xml(file_name, check_exists=True):
    """Returns a parsed xml tree with comments intact."""
    error_message = ''
    if check_exists and not os.path.exists(file_name):
        return None, "File does not exist %s" % str(file_name)

    with open(file_name, 'r') as fobj:
        try:
            tree = XmlET.parse(fobj, parser=XmlET.XMLParser(target=CommentedTreeBuilder()))
        except Exception as e:
            error_message = "Exception attempting to parse %s: %s" % (str(file_name), str(e))
            log.exception(error_message)
            return None, error_message
    return tree, error_message