def get_raw_out():

    local_path = pwndbg.file.get_file(pwndbg.proc.exe)
    cmd = [get_raw_out.cmd_path, "--file", local_path]
    return pwndbg.wrappers.call_cmd(cmd)