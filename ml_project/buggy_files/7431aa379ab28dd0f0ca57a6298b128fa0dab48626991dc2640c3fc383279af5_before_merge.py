    def play(self, board, limit, *, game=None, info=INFO_NONE, ponder=False, root_moves=None, options={}):
        if root_moves is not None:
            raise EngineError("play with root_moves, but xboard supports include only in analysis mode")

        class Command(BaseCommand):
            def start(self, engine):
                self.info = {}
                self.stopped = False
                self.final_pong = None
                self.draw_offered = False

                # Set game, position and configure.
                engine._new(board, game, options)

                # Limit or time control.
                increment = limit.white_inc if board.turn else limit.black_inc
                if limit.remaining_moves or increment:
                    base_mins, base_secs = divmod(int(limit.white_clock if board.turn else limit.black_clock), 60)
                    engine.send_line("level {} {}:{:02d} {}".format(limit.remaining_moves or 0, base_mins, base_secs, increment))

                if limit.nodes is not None:
                    if limit.time is not None or limit.white_clock is not None or limit.black_clock is not None or increment is not None:
                        raise EngineError("xboard does not support mixing node limits with time limits")

                    if "nps" not in engine.features:
                        LOGGER.warning("%s: Engine did not declare explicit support for node limits (feature nps=?)")
                    elif not engine.features["nps"]:
                        raise EngineError("xboard engine does not support node limits (feature nps=0)")

                    engine.send_line("nps 1")
                    engine.send_line("st {}".format(int(limit.nodes)))
                if limit.depth is not None:
                    engine.send_line("sd {}".format(limit.depth))
                if limit.time is not None:
                    engine.send_line("st {}".format(limit.time))
                if limit.white_clock is not None:
                    engine.send_line("{} {}".format("time" if board.turn else "otim", int(limit.white_clock * 100)))
                if limit.black_clock is not None:
                    engine.send_line("{} {}".format("otim" if board.turn else "time", int(limit.black_clock * 100)))

                # Start thinking.
                engine.send_line("post" if info else "nopost")
                engine.send_line("hard" if ponder else "easy")
                engine.send_line("go")

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

            def _post(self, engine, line):
                if not self.result.done():
                    self.info = _parse_xboard_post(line, engine.board, info)

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

            def end(self, engine):
                self.set_finished()

        return (yield from self.communicate(Command))