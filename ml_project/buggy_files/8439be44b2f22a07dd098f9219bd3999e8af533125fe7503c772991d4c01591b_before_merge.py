    def wait_for_active_job(last_task=None, backgrounded=False):
        """
        Wait for the active job to finish, to be killed by SIGINT, or to be
        suspended by ctrl-z.
        """
        _clear_dead_jobs()
        active_task = get_next_task()
        # Return when there are no foreground active task
        if active_task is None:
            _give_terminal_to(_shell_pgrp)  # give terminal back to the shell
            if backgrounded and hasattr(builtins, '__xonsh_shell__'):
                # restoring sanity could probably be called whenever we return
                # control to the shell. But it only seems to matter after a
                # ^Z event. This *has* to be called after we give the terminal
                # back to the shell.
                builtins.__xonsh_shell__.shell.restore_tty_sanity()
            return last_task
        pgrp = active_task.get('pgrp', None)
        obj = active_task['obj']
        backgrounded = False
        # give the terminal over to the fg process
        if pgrp is not None:
            _give_terminal_to(pgrp)
        _continue(active_task)
        _, wcode = os.waitpid(obj.pid, os.WUNTRACED)
        if os.WIFSTOPPED(wcode):
            print('^Z')
            active_task['status'] = "stopped"
            backgrounded = True
        elif os.WIFSIGNALED(wcode):
            print()  # get a newline because ^C will have been printed
            obj.signal = (os.WTERMSIG(wcode), os.WCOREDUMP(wcode))
            obj.returncode = None
        else:
            obj.returncode = os.WEXITSTATUS(wcode)
            obj.signal = None
        return wait_for_active_job(last_task=active_task,
                                   backgrounded=backgrounded)