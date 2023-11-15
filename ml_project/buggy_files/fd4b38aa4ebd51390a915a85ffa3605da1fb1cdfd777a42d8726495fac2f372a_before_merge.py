def exec_code_all(lang, code, cwd=None):
    '''
    Pass in two strings, the first naming the executable language, aka -
    python2, python3, ruby, perl, lua, etc. the second string containing
    the code you wish to execute. All cmd artifacts (stdout, stderr, retcode, pid)
    will be returned.

    CLI Example:

    .. code-block:: bash

        salt '*' cmd.exec_code_all ruby 'puts "cheese"'
    '''
    codefile = salt.utils.mkstemp()
    with salt.utils.fopen(codefile, 'w+t') as fp_:
        fp_.write(code)
    cmd = [lang, codefile]
    ret = run_all(cmd, cwd=cwd, python_shell=False)
    os.remove(codefile)
    return ret