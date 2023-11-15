    def monitor_wrapper(f,
                        try_id,
                        task_id,
                        monitoring_hub_url,
                        run_id,
                        logging_level,
                        sleep_dur):
        """ Internal
        Wrap the Parsl app with a function that will call the monitor function and point it at the correct pid when the task begins.
        """
        def wrapped(*args, **kwargs):
            command_q = Queue(maxsize=10)
            p = Process(target=monitor,
                        args=(os.getpid(),
                              try_id,
                              task_id,
                              monitoring_hub_url,
                              run_id,
                              command_q,
                              logging_level,
                              sleep_dur),
                        name="Monitor-Wrapper-{}".format(task_id))
            p.start()
            try:
                try:
                    return f(*args, **kwargs)
                finally:
                    command_q.put("Finished")
                    p.join()
            finally:
                # There's a chance of zombification if the workers are killed by some signals
                p.terminate()
                p.join()
        return wrapped