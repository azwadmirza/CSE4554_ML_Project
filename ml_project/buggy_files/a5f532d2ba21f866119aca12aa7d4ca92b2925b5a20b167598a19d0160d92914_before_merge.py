    def __enter__(self):
        # Keep the string "LOCKERROR" in this string so that external
        # programs can look for it.
        lockstr = ("""\
    LOCKERROR: It looks like conda is already doing something.
    The lock %s was found. Wait for it to finish before continuing.
    If you are sure that conda is not running, remove it and try again.
    You can also use: $ conda clean --lock\n""")
        sleeptime = 1

        for _ in range(self.retries):
            if os.path.isdir(self.lock_path):
                stdoutlog.info(lockstr % self.lock_path)
                stdoutlog.info("Sleeping for %s seconds\n" % sleeptime)

                time.sleep(sleeptime)
                sleeptime *= 2
            else:
                os.makedirs(self.lock_path)
                return self

        stdoutlog.error("Exceeded max retries, giving up")
        raise LockError(lockstr % self.lock_path)