            def stop(self):
                self.Terminated = True
                while not self.q.empty():
                    self.q.get()