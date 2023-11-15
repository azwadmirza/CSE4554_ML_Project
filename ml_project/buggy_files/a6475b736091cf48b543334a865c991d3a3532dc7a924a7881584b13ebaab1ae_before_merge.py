            def cancel(self, engine):
                if self.stopped:
                    return
                self.stopped = True

                if self.result.cancelled():
                    engine.send_line("?")

                if ponder:
                    engine.send_line("easy")

                    n = id(self) & 0xffff
                    self.final_pong = "pong {}".format(n)
                    engine._ping(n)