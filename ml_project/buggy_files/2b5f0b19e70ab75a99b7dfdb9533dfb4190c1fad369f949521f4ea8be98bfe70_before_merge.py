def token_list(kubeconfig=None, rootfs=None):
    """
    .. versionadded:: TBD

    List bootstrap tokens on the server

    kubeconfig
       The kubeconfig file to use when talking to the cluster. The
       default values in /etc/kubernetes/admin.conf

    rootfs
       The path to the real host root filesystem

    CLI Example:

    .. code-block:: bash

       salt '*' kubeadm.token_list

    """
    cmd = ["kubeadm", "token", "list"]

    parameters = [("kubeconfig", kubeconfig), ("rootfs", rootfs)]
    for parameter, value in parameters:
        if value:
            cmd.extend(["--{}".format(parameter), str(value)])

    lines = _cmd(cmd).splitlines()

    # Find the header and parse it.  We do not need to validate the
    # content, as the regex will take care of future changes.
    header = lines.pop(0)
    header = [i.lower() for i in re.findall(r"(\w+(?:\s\w+)*)", header)]

    tokens = []
    for line in lines:
        # TODO(aplanas): descriptions with multiple spaces can break
        # the parser.
        values = re.findall(r"(\S+(?:\s\S+)*)", line)
        if len(header) != len(values):
            log.error("Error parsing line: {}".format(line))
            continue
        tokens.append({key: value for key, value in zip(header, values)})
    return tokens