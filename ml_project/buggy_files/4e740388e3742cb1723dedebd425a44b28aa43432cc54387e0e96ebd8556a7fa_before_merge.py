def fcontext_get_policy(name, filetype=None, sel_type=None, sel_user=None, sel_level=None):
    '''
    Returns the current entry in the SELinux policy list as a dictionary.
    Returns None if no exact match was found
    Returned keys are:
    - filespec (the name supplied and matched)
    - filetype (the descriptive name of the filetype supplied)
    - sel_user, sel_role, sel_type, sel_level (the selinux context)
    For a more in-depth explanation of the selinux context, go to
    https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/6/html/Security-Enhanced_Linux/chap-Security-Enhanced_Linux-SELinux_Contexts.html

    name: filespec of the file or directory. Regex syntax is allowed.
    filetype: The SELinux filetype specification.
              Use one of [a, f, d, c, b, s, l, p].
              See also `man semanage-fcontext`.
              Defaults to 'a' (all files)

    CLI Example:

    .. code-block:: bash

        salt '*' selinux.fcontext_get_policy my-policy
    '''
    if filetype:
        _validate_filetype(filetype)
    re_spacer = '[ ]{2,}'
    cmd_kwargs = {'spacer': re_spacer,
                  'filespec': re.escape(name),
                  'sel_user': sel_user or '[^:]+',
                  'sel_role': '[^:]+',  # se_role for file context is always object_r
                  'sel_type': sel_type or '[^:]+',
                  'sel_level': sel_level or '[^:]+'}
    cmd_kwargs['filetype'] = '[[:alpha:] ]+' if filetype is None else _filetype_id_to_string(filetype)
    cmd = 'semanage fcontext -l | egrep ' + \
          "'^{filespec}{spacer}{filetype}{spacer}{sel_user}:{sel_role}:{sel_type}:{sel_level}$'".format(**cmd_kwargs)
    current_entry_text = __salt__['cmd.shell'](cmd)
    if current_entry_text == '':
        return None
    ret = {}
    current_entry_list = re.split(re_spacer, current_entry_text)
    ret['filespec'] = current_entry_list[0]
    ret['filetype'] = current_entry_list[1]
    ret.update(_context_string_to_dict(current_entry_list[2]))
    return ret