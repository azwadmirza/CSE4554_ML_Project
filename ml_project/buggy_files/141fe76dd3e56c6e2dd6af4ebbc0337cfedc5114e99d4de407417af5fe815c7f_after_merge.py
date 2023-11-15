def _exec_query_ps(cmd, fields):
    """Execute a PowerShell query, using the cmd command,
    and select and parse the provided fields.
    """
    if not conf.prog.powershell:
        raise OSError("Scapy could not detect powershell !")
    # Build query
    query_cmd = cmd + ['|', 'select %s' % ', '.join(fields),  # select fields
                       '|', 'fl',  # print as a list
                       '|', 'out-string', '-Width', '4096']  # do not crop
    lines = []
    # Ask the powershell manager to process the query
    stdout = POWERSHELL_PROCESS.query(query_cmd)
    # Process stdout
    for line in stdout:
        if not line.strip():  # skip empty lines
            continue
        sl = line.split(':', 1)
        if sl[0].strip() not in fields:
            # The previous line was cropped. Let's add the missing part
            lines[-1] += line.strip()
            continue
        else:
            # We put it here to ensure we never return too early,
            # missing some cropped lines
            if len(lines) == len(fields):
                yield lines
                lines = []
            lines.append(sl[1].strip())
    yield lines  # Last buffer won't be returned in the if