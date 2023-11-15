    def __init__(self, message=None, **kwargs):
        if not message:
            message = "Failed to create virtual environment."
        self.message = message
        VirtualenvException.__init__(self, decode_for_output(message), **kwargs)