    def __init__(self, reply_func, script_thread):
        self.reply_func = reply_func
        self.script_thread = script_thread
        self.master_reply = None