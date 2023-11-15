    def cancel_request(self):
        if self.reply:
            self.reply.abort()