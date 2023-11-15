            def line_received(self, engine, line):
                if line.startswith("move "):
                    self._move(engine, line.split(" ", 1)[1])
                elif line == self.final_pong:
                    if not self.result.done():
                        self.result.set_exception(EngineError("xboard engine answered final pong before sending move"))
                    self.end(engine)
                elif line == "offer draw":
                    self.draw_offered = True
                elif line == "resign":
                    self.result.set_result(PlayResult(None, None, self.info, draw_offered=self.draw_offered, resigned=True))
                    self.end(engine)
                elif line.startswith("1-0") or line.startswith("0-1") or line.startswith("1/2-1/2"):
                    if not self.result.done():
                        self.result.set_result(PlayResult(None, None, self.info, draw_offered=self.draw_offered))
                    self.end(engine)
                elif line.startswith("#") or line.startswith("Hint:"):
                    pass
                elif len(line.split()) >= 4 and line.lstrip()[0].isdigit():
                    self._post(engine, line)
                else:
                    LOGGER.warning("%s: Unexpected engine output: %s", engine, line)