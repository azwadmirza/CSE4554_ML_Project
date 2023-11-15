    def __init__(self, original_reply, script_thread):
        self.original_reply = original_reply
        self.script_thread = script_thread
        self._ignore_call = True
        self.lock = threading.Lock()