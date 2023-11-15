def run_python_script_in_terminal(fname, wdir, args, interact,
                                  debug, python_args):
    """
    Run Python script in an external system terminal.

    :str wdir: working directory, may be empty.
    """
    
    # If fname has spaces on it it can't be ran on Windows, so we have to
    # enclose it in quotes. Also wdir can come with / as os.sep, so we
    # need to take care of it
    if os.name == 'nt':
        fname = '"' + fname + '"'
        wdir = wdir.replace('/', '\\')
    
    p_args = ['python']
    p_args += get_python_args(fname, python_args, interact, debug, args)
    
    if os.name == 'nt':
        cmd = 'start cmd.exe /c "cd %s && ' % wdir + ' '.join(p_args) + '"'
        # Command line and cwd have to be converted to the filesystem
        # encoding before passing them to subprocess, but only for
        # Python 2.
        # See http://bugs.python.org/issue1759845#msg74142 and Issue 1856
        if PY2:
            cmd = encoding.to_fs_from_unicode(cmd)
            wdir = encoding.to_fs_from_unicode(wdir)
        try:
            run_shell_command(cmd, cwd=wdir)
        except WindowsError:
            from qtpy.QtWidgets import QMessageBox

            from spyderlib.config.base import _

            QMessageBox.critical(None, _('Run'),
                                 _("It was not possible to run this file in "
                                   "an external terminal"),
                                 QMessageBox.Ok)
    elif os.name == 'posix':
        programs = [{'cmd': 'gnome-terminal',
                     'wdir-option': '--working-directory',
                     'execute-option': '-x'},
                    {'cmd': 'konsole',
                     'wdir-option': '--workdir',
                     'execute-option': '-e'},
                    {'cmd': 'xfce4-terminal',
                     'wdir-option': '--working-directory',
                     'execute-option': '-x'},
                    {'cmd': 'xterm',
                     'wdir-option': None,
                     'execute-option': '-e'},]
        for program in programs:
            if is_program_installed(program['cmd']):
                arglist = []
                if program['wdir-option'] and wdir:
                    arglist += [program['wdir-option'], wdir]
                arglist.append(program['execute-option'])
                arglist += p_args
                if wdir:
                    run_program(program['cmd'], arglist, cwd=wdir)
                else:
                    run_program(program['cmd'], arglist)
                return
        # TODO: Add a fallback to OSX
    else:
        raise NotImplementedError