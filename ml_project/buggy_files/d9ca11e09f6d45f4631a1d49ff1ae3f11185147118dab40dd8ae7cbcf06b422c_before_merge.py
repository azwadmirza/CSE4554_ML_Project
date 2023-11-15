            def stop(self):
                self.Terminated = True
                msvcrt.putch(' ')
                while not self.q.empty():
                    self.q.get()