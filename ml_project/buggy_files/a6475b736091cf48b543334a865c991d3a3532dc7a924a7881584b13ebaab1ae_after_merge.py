            def cancel(self, engine):
                if self.stopped:
                    return
                self.stopped = True

                if self.result.cancelled():
                    engine.send_line("?")

                if ponder:
                    engine.send_line("easy")

                    n = (id(self) + 1) & 0xffff
                    self.pong_after_ponder = "pong {}".format(n)
                    engine._ping(n)