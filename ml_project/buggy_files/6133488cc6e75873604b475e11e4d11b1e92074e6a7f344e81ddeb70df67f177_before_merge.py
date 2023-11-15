            def _move(self, engine, arg):
                if not self.result.cancelled():
                    try:
                        move = engine.board.push_xboard(arg)
                    except ValueError as err:
                        self.result.set_exception(EngineError(err))
                    else:
                        self.result.set_result(PlayResult(move, None, self.info, draw_offered=self.draw_offered))

                if not ponder:
                    self.end(engine)