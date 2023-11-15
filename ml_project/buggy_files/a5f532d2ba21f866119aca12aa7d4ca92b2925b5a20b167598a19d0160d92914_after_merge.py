    def __enter__(self):
        retries = 10
        # Keep the string "LOCKERROR" in this string so that external
        # programs can look for it.
        lockstr = ("""\
    LOCKERROR: It looks like conda is already doing something.
    The lock %s was found. Wait for it to finish before continuing.
    If you are sure that conda is not running, remove it and try again.
    You can also use: $ conda clean --lock\n""")
        sleeptime = 1
        files = None
        while retries:
            files = glob.glob(self.pattern)
            if files and not files[0].endswith(self.end):
                stdoutlog.info(lockstr % str(files))
                stdoutlog.info("Sleeping for %s seconds\n" % sleeptime)
                sleep(sleeptime)
                sleeptime *= 2
                retries -= 1
            else:
                break
        else:
            stdoutlog.error("Exceeded max retries, giving up")
            raise RuntimeError(lockstr % str(files))

        if not files:
            try:
                os.makedirs(self.lock_path)
            except OSError:
                pass
        else:  # PID lock already here --- someone else will remove it.
            self.remove = False