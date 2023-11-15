def get_raw_out():
    local_path = pwndbg.file.get_file(pwndbg.proc.exe)
    try:
        version_output = subprocess.check_output([get_raw_out.cmd_path, "--version"], stderr=STDOUT).decode('utf-8')
        match = search('checksec v([\\w.]+),', version_output)
        if match:
            version = tuple(map(int, (match.group(1).split("."))))
            if version >= (2, 0):
                return pwndbg.wrappers.call_cmd([get_raw_out.cmd_path, "--file=" + local_path])
    except Exception:
        pass
    return pwndbg.wrappers.call_cmd([get_raw_out.cmd_path, "--file", local_path])