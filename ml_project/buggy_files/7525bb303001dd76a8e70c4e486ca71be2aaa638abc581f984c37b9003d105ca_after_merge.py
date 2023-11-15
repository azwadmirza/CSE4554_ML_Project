def dnf_autoremove():
    """Run 'dnf autoremove' and return size in bytes recovered"""
    if os.path.exists('/var/run/dnf.pid'):
        msg = _(
            "%s cannot be cleaned because it is currently running.  Close it, and try again.") % "Dnf"
        raise RuntimeError(msg)
    cmd = ['dnf', '-y', 'autoremove']
    process = subprocess.Popen(
        cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    freed_bytes = 0
    while True:
        line = process.stdout.readline().decode(
            bleachbit.stdout_encoding).replace("\n", "")
        if 'Error: This command has to be run under the root user.' == line:
            raise RuntimeError('dnf autoremove >> requires root permissions')
        if 'Nothing to do.' == line:
            break
        cregex = re.compile("Freed space: ([\d.]+[\s]+[BkMG])")
        match = cregex.search(line)
        if match:
            freed_bytes = parseSize(match.group(1))
            break
        if "" == line and process.poll() != None:
            break
    logger.debug(
        'dnf_autoremove >> total freed bytes: %s', freed_bytes)
    return freed_bytes