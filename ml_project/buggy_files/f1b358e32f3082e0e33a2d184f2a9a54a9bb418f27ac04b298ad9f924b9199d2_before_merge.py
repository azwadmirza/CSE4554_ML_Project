def _gluster_output_cleanup(result):
    """
    Gluster versions prior to 6 have a bug that requires tricking
    isatty. This adds "gluster> " to the output. Strip it off and
    produce clean xml for ElementTree.
    """
    ret = ""
    for line in result.splitlines():
        if line.startswith("gluster>"):
            ret += line[9:].strip()
        else:
            ret += line.strip()

    return ret