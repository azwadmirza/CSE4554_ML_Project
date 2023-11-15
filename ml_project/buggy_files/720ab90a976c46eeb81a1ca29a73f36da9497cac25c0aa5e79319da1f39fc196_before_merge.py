            def _post(self, engine, line):
                if not self.result.done():
                    self.info = _parse_xboard_post(line, engine.board, info)