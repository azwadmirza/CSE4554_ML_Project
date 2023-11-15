def modify_module(module_name, module_path, module_args, task_vars=None, templar=None, module_compression='ZIP_STORED', async_timeout=0, become=False,
                  become_method=None, become_user=None, become_password=None, environment=None):
    """
    Used to insert chunks of code into modules before transfer rather than
    doing regular python imports.  This allows for more efficient transfer in
    a non-bootstrapping scenario by not moving extra files over the wire and
    also takes care of embedding arguments in the transferred modules.

    This version is done in such a way that local imports can still be
    used in the module code, so IDEs don't have to be aware of what is going on.

    Example:

    from ansible.module_utils.basic import *

       ... will result in the insertion of basic.py into the module
       from the module_utils/ directory in the source tree.

    For powershell, this code effectively no-ops, as the exec wrapper requires access to a number of
    properties not available here.

    """
    task_vars = {} if task_vars is None else task_vars
    environment = {} if environment is None else environment

    with open(module_path, 'rb') as f:

        # read in the module source
        b_module_data = f.read()

    (b_module_data, module_style, shebang) = _find_module_utils(module_name, b_module_data, module_path, module_args, task_vars, templar, module_compression,
                                                                async_timeout=async_timeout, become=become, become_method=become_method,
                                                                become_user=become_user, become_password=become_password,
                                                                environment=environment)

    if module_style == 'binary':
        return (b_module_data, module_style, to_text(shebang, nonstring='passthru'))
    elif shebang is None:
        lines = b_module_data.split(b"\n", 1)
        if lines[0].startswith(b"#!"):
            shebang = lines[0].strip()
            args = shlex.split(str(shebang[2:]))
            interpreter = args[0]
            interpreter = to_bytes(interpreter)

            new_shebang = to_bytes(_get_shebang(interpreter, task_vars, templar, args[1:])[0], errors='surrogate_or_strict', nonstring='passthru')
            if new_shebang:
                lines[0] = shebang = new_shebang

            if os.path.basename(interpreter).startswith(b'python'):
                lines.insert(1, to_bytes(ENCODING_STRING))
        else:
            # No shebang, assume a binary module?
            pass

        b_module_data = b"\n".join(lines)
    else:
        shebang = to_bytes(shebang, errors='surrogate_or_strict')

    return (b_module_data, module_style, to_text(shebang, nonstring='passthru'))