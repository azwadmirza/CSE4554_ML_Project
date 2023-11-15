    def wait_for_active_job():
        """
        Wait for the active job to finish, to be killed by SIGINT, or to be
        suspended by ctrl-z.
        """
        _clear_dead_jobs()
        active_task = get_next_task()
        # Return when there are no foreground active task
        if active_task is None:
            _give_terminal_to(_shell_pgrp)  # give terminal back to the shell
            return
        pgrp = active_task.get('pgrp', None)
        obj = active_task['obj']
        # give the terminal over to the fg process
        if pgrp is not None:
            _give_terminal_to(pgrp)
        _continue(active_task)
        _, wcode = os.waitpid(obj.pid, os.WUNTRACED)
        if os.WIFSTOPPED(wcode):
            print()  # get a newline because ^Z will have been printed
            active_task['status'] = "stopped"
        elif os.WIFSIGNALED(wcode):
            print()  # get a newline because ^C will have been printed
            obj.signal = (os.WTERMSIG(wcode), os.WCOREDUMP(wcode))
            obj.returncode = None
        else:
            obj.returncode = os.WEXITSTATUS(wcode)
            obj.signal = None
        return wait_for_active_job()