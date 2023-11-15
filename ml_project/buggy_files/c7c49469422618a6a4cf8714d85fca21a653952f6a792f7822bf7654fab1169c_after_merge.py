            def line_received(self, engine, line):
                if line.startswith("move "):
                    self._move(engine, line.split(" ", 1)[1])
                elif line.startswith("Hint: "):
                    self._hint(engine, line.split(" ", 1)[1])
                elif line == self.pong_after_move:
                    if not self.result.done():
                        self.result.set_result(self.play_result)
                    if not ponder:
                        self.set_finished()
                elif line == self.pong_after_ponder:
                    if not self.result.done():
                        self.result.set_result(self.play_result)
                    self.set_finished()
                elif line == "offer draw":
                    if not self.result.done():
                        self.play_result.draw_offered = True
                    self._ping_after_move(engine)
                elif line == "resign":
                    if not self.result.done():
                        self.play_result.resigned = True
                    self._ping_after_move(engine)
                elif line.startswith("1-0") or line.startswith("0-1") or line.startswith("1/2-1/2"):
                    self._ping_after_move(engine)
                elif line.startswith("#"):
                    pass
                elif len(line.split()) >= 4 and line.lstrip()[0].isdigit():
                    self._post(engine, line)
                else:
                    LOGGER.warning("%s: Unexpected engine output: %s", engine, line)