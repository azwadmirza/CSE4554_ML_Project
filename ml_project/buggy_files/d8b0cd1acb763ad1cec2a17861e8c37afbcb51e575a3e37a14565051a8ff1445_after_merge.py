def _get_config_file(conf, atom):
    '''
    Parse the given atom, allowing access to its parts
    Success does not mean that the atom exists, just that it
    is in the correct format.
    Returns none if the atom is invalid.
    '''
    if '*' in atom:
        parts = portage.dep.Atom(atom, allow_wildcard=True)
        if not parts:
            return
        if parts.cp == '*/*':
            # parts.repo will be empty if there is no repo part
            relative_path = parts.repo or "gentoo"
        elif str(parts.cp).endswith('/*'):
            relative_path = str(parts.cp).split("/")[0] + "_"
        else:
            relative_path = os.path.join(*[x for x in os.path.split(parts.cp) if x != '*'])
    else:
        relative_path = _p_to_cp(atom)
        if not relative_path:
            return

    complete_file_path = BASE_PATH.format(conf) + '/' + relative_path

    return complete_file_path