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
            # Send first message to monitoring router
            try:
                monitor(os.getpid(),
                        task_id,
                        monitoring_hub_url,
                        run_id,
                        logging_level,
                        sleep_dur,
                        first_message=True)
            except Exception:
                pass

            # create the monitor process and start
            p = Process(target=monitor,
                        args=(os.getpid(),
                              try_id,
                              task_id,
                              monitoring_hub_url,
                              run_id,
                              logging_level,
                              sleep_dur),
                        name="Monitor-Wrapper-{}".format(task_id))
            p.start()

            try:
                return f(*args, **kwargs)
            finally:
                # There's a chance of zombification if the workers are killed by some signals
                p.terminate()
                p.join()
        return wrapped