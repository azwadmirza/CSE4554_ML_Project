def run_python_script_in_terminal(fname, wdir, args, interact,
                                  debug, python_args):
    """Run Python script in an external system terminal"""
    
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
        cmd = 'gnome-terminal'
        if is_program_installed(cmd):
            run_program(cmd, ['--working-directory', wdir, '-x'] + p_args,
                        cwd=wdir)
            return
        cmd = 'konsole'
        if is_program_installed(cmd):
            run_program(cmd, ['--workdir', wdir, '-e'] + p_args,
                        cwd=wdir)
            return
        cmd = 'xfce4-terminal'
        if is_program_installed(cmd):
            run_program(cmd, ['--working-directory', wdir, '-x'] + p_args,
                        cwd=wdir)
            return
        cmd = 'xterm'
        if is_program_installed(cmd):
            run_program(cmd, ['-e'] + p_args + [wdir])
            return		
        # TODO: Add a fallback to OSX
    else:
        raise NotImplementedError