def _find_snippet_imports(module_name, module_data, module_path, module_args, task_vars, module_compression):
    """
    Given the source of the module, convert it to a Jinja2 template to insert
    module code and return whether it's a new or old style module.
    """

    module_substyle = module_style = 'old'

    # module_style is something important to calling code (ActionBase).  It
    # determines how arguments are formatted (json vs k=v) and whether
    # a separate arguments file needs to be sent over the wire.
    # module_substyle is extra information that's useful internally.  It tells
    # us what we have to look to substitute in the module files and whether
    # we're using module replacer or ziploader to format the module itself.
    if REPLACER in module_data:
        # Do REPLACER before from ansible.module_utils because we need make sure
        # we substitute "from ansible.module_utils basic" for REPLACER
        module_style = 'new'
        module_substyle = 'python'
        module_data = module_data.replace(REPLACER, b'from ansible.module_utils.basic import *')
    elif b'from ansible.module_utils.' in module_data:
        module_style = 'new'
        module_substyle = 'python'
    elif REPLACER_WINDOWS in module_data:
        module_style = 'new'
        module_substyle = 'powershell'
    elif REPLACER_JSONARGS in module_data:
        module_style = 'new'
        module_substyle = 'jsonargs'
    elif b'WANT_JSON' in module_data:
        module_substyle = module_style = 'non_native_want_json'

    shebang = None
    # Neither old-style nor non_native_want_json modules should be modified
    # except for the shebang line (Done by modify_module)
    if module_style in ('old', 'non_native_want_json'):
        return module_data, module_style, shebang

    output = BytesIO()
    py_module_names = set()

    if module_substyle == 'python':
        # ziploader for new-style python classes
        constants = dict(
                SELINUX_SPECIAL_FS=C.DEFAULT_SELINUX_SPECIAL_FS,
                SYSLOG_FACILITY=_get_facility(task_vars),
                )
        params = dict(ANSIBLE_MODULE_ARGS=module_args,
                ANSIBLE_MODULE_CONSTANTS=constants,
                )
        python_repred_params = to_bytes(repr(json.dumps(params)), errors='strict')

        try:
            compression_method = getattr(zipfile, module_compression)
        except AttributeError:
            display.warning(u'Bad module compression string specified: %s.  Using ZIP_STORED (no compression)' % module_compression)
            compression_method = zipfile.ZIP_STORED

        lookup_path = os.path.join(C.DEFAULT_LOCAL_TMP, 'ziploader_cache')
        cached_module_filename = os.path.join(lookup_path, "%s-%s" % (module_name, module_compression))

        zipdata = None
        # Optimization -- don't lock if the module has already been cached
        if os.path.exists(cached_module_filename):
            zipdata = open(cached_module_filename, 'rb').read()
            # Fool the check later... I think we should just remove the check
            py_module_names.add(('basic',))
        else:
            with action_write_locks[module_name]:
                # Check that no other process has created this while we were
                # waiting for the lock
                if not os.path.exists(cached_module_filename):
                    # Create the module zip data
                    zipoutput = BytesIO()
                    zf = zipfile.ZipFile(zipoutput, mode='w', compression=compression_method)
                    zf.writestr('ansible/__init__.py', b''.join((b"__version__ = '", to_bytes(__version__), b"'\n")))
                    zf.writestr('ansible/module_utils/__init__.py', b'')

                    zf.writestr('ansible_module_%s.py' % module_name, module_data)

                    py_module_cache = { ('__init__',): b'' }
                    recursive_finder(module_name, module_data, py_module_names, py_module_cache, zf)
                    zf.close()
                    zipdata = base64.b64encode(zipoutput.getvalue())

                    # Write the assembled module to a temp file (write to temp
                    # so that no one looking for the file reads a partially
                    # written file)
                    if not os.path.exists(lookup_path):
                        # Note -- if we have a global function to setup, that would
                        # be a better place to run this
                        os.mkdir(lookup_path)
                    with open(cached_module_filename + '-part', 'w') as f:
                        f.write(zipdata)

                    # Rename the file into its final position in the cache so
                    # future users of this module can read it off the
                    # filesystem instead of constructing from scratch.
                    os.rename(cached_module_filename + '-part', cached_module_filename)

            if zipdata is None:
                # Another process wrote the file while we were waiting for
                # the write lock.  Go ahead and read the data from disk
                # instead of re-creating it.
                try:
                    zipdata = open(cached_module_filename, 'rb').read()
                except IOError:
                    raise AnsibleError('A different worker process failed to create module file.  Look at traceback for that process for debugging information.')
                # Fool the check later... I think we should just remove the check
                py_module_names.add(('basic',))

        shebang, interpreter = _get_shebang(u'/usr/bin/python', task_vars)
        if shebang is None:
            shebang = u'#!/usr/bin/python'

        executable = interpreter.split(u' ', 1)
        if len(executable) == 2 and executable[0].endswith(u'env'):
            # Handle /usr/bin/env python style interpreter settings
            interpreter = u"'{0}', '{1}'".format(*executable)
        else:
            # Still have to enclose the parts of the interpreter in quotes
            # because we're substituting it into the template as a python
            # string
            interpreter = u"'{0}'".format(interpreter)

        output.write(to_bytes(ACTIVE_ZIPLOADER_TEMPLATE % dict(
            zipdata=zipdata,
            ansible_module=module_name,
            params=python_repred_params,
            shebang=shebang,
            interpreter=interpreter,
            coding=ENCODING_STRING,
            )))
        module_data = output.getvalue()

        # Sanity check from 1.x days.  Maybe too strict.  Some custom python
        # modules that use ziploader may implement their own helpers and not
        # need basic.py.  All the constants that we substituted into basic.py
        # for module_replacer are now available in other, better ways.
        if ('basic',) not in py_module_names:
            raise AnsibleError("missing required import in %s: Did not import ansible.module_utils.basic for boilerplate helper code" % module_path)

    elif module_substyle == 'powershell':
        # Module replacer for jsonargs and windows
        lines = module_data.split(b'\n')
        for line in lines:
            if REPLACER_WINDOWS in line:
                ps_data = _slurp(os.path.join(_SNIPPET_PATH, "powershell.ps1"))
                output.write(ps_data)
                py_module_names.add((b'powershell',))
                continue
            output.write(line + b'\n')
        module_data = output.getvalue()

        module_args_json = to_bytes(json.dumps(module_args))
        module_data = module_data.replace(REPLACER_JSONARGS, module_args_json)

        # Sanity check from 1.x days.  This is currently useless as we only
        # get here if we are going to substitute powershell.ps1 into the
        # module anyway.  Leaving it for when/if we add other powershell
        # module_utils files.
        if (b'powershell',) not in py_module_names:
            raise AnsibleError("missing required import in %s: # POWERSHELL_COMMON" % module_path)

    elif module_substyle == 'jsonargs':
        module_args_json = to_bytes(json.dumps(module_args))

        # these strings could be included in a third-party module but
        # officially they were included in the 'basic' snippet for new-style
        # python modules (which has been replaced with something else in
        # ziploader) If we remove them from jsonargs-style module replacer
        # then we can remove them everywhere.
        python_repred_args = to_bytes(repr(module_args_json))
        module_data = module_data.replace(REPLACER_VERSION, to_bytes(repr(__version__)))
        module_data = module_data.replace(REPLACER_COMPLEX, python_repred_args)
        module_data = module_data.replace(REPLACER_SELINUX, to_bytes(','.join(C.DEFAULT_SELINUX_SPECIAL_FS)))

        # The main event -- substitute the JSON args string into the module
        module_data = module_data.replace(REPLACER_JSONARGS, module_args_json)

        facility = b'syslog.' + to_bytes(_get_facility(task_vars), errors='strict')
        module_data = module_data.replace(b'syslog.LOG_USER', facility)

    return (module_data, module_style, shebang)