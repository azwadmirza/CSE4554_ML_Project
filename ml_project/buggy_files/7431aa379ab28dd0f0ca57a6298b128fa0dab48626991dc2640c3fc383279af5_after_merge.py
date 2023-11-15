    def play(self, board, limit, *, game=None, info=INFO_NONE, ponder=False, root_moves=None, options={}):
        if root_moves is not None:
            raise EngineError("play with root_moves, but xboard supports 'include' only in analysis mode")

        class Command(BaseCommand):
            def start(self, engine):
                self.play_result = PlayResult(None, None)
                self.stopped = False
                self.pong_after_move = None
                self.pong_after_ponder = None

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

            def _post(self, engine, line):
                if not self.result.done():
                    self.play_result.info = _parse_xboard_post(line, engine.board, info)

            def _move(self, engine, arg):
                if not self.result.done() and self.play_result.move is None:
                    try:
                        self.play_result.move = engine.board.push_xboard(arg)
                    except ValueError as err:
                        self.result.set_exception(EngineError(err))
                    else:
                        self._ping_after_move(engine)
                else:
                    try:
                        engine.board.push_xboard(arg)
                    except ValueError:
                        LOGGER.exception("exception playing unexpected move")

            def _hint(self, engine, arg):
                if not self.result.done() and self.play_result.move is not None and self.play_result.ponder is None:
                    try:
                        self.play_result.ponder = engine.board.parse_xboard(arg)
                    except ValueError:
                        LOGGER.exception("exception parsing hint")
                else:
                    LOGGER.warning("unexpected hint: %r", arg)

            def _ping_after_move(self, engine):
                if self.pong_after_move is None:
                    n = id(self) & 0xffff
                    self.pong_after_move = "pong {}".format(n)
                    engine._ping(n)

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

        return (yield from self.communicate(Command))