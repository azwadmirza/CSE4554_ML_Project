    def __call__(self, *args):
        if self.master_reply is None:
            self.master_reply = args
            self.script_thread.start()
            return
        self.reply_func(*args)