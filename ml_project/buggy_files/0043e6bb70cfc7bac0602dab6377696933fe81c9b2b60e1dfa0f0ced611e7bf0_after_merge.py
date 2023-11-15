    def free_binding(self, guest_id):
        self.lock.acquire()
        try:
            self.bindings[guest_id][0] -= 1

            # stop listening if no one is connected
            if self.bindings[guest_id][0] <= 0:
                self.bindings[guest_id][1].stopListening()
                self.bindings[guest_id][2].stopListening()
                del self.bindings[guest_id]
        finally:
            self.lock.release()