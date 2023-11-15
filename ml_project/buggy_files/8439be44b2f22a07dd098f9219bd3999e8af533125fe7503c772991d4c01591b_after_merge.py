    def wait_for_active_job(last_task=None, backgrounded=False):
        """
        Wait for the active job to finish, to be killed by SIGINT, or to be
        suspended by ctrl-z.
        """
        _clear_dead_jobs()
        active_task = get_next_task()
        # Return when there are no foreground active task
        if active_task is None:
            return last_task
        obj = active_task['obj']
        backgrounded = False
        try:
            _, wcode = os.waitpid(obj.pid, os.WUNTRACED)
        except ChildProcessError:  # No child processes
            return wait_for_active_job(last_task=active_task,
                                       backgrounded=backgrounded)
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