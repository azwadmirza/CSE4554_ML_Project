def run_vcs_tool(path, action):
    """If path is a valid VCS repository, run the corresponding VCS tool
    Supported VCS actions: 'commit', 'browse'
    Return False if the VCS tool is not installed"""
    info = get_vcs_info(get_vcs_root(path))
    tools = info['actions'][action]
    for tool, args in tools:
        if programs.find_program(tool):
            programs.run_program(tool, args, cwd=path)
            return
    else:
        cmdnames = [name for name, args in tools]
        raise ActionToolNotFound(info['name'], action, cmdnames)