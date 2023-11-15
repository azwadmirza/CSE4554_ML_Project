    def _do_draw(self, screen):  # pragma: no cover
        from asciimatics.event import KeyboardEvent

        offset_x = 0
        offset_y = 0
        smaxrow, smaxcol = screen.dimensions
        assert smaxrow > 1
        assert smaxcol > 1
        smaxrow -= 1
        smaxcol -= 1

        if self.lines + 1 > smaxrow:
            max_y = self.lines + 1 - smaxrow
        else:
            max_y = 0

        if self.cols + 1 > smaxcol:
            max_x = self.cols + 1 - smaxcol
        else:
            max_x = 0

        while True:
            for y in range(smaxrow + 1):
                y_index = offset_y + y
                line = []
                for x in range(smaxcol + 1):
                    x_index = offset_x + x
                    if len(self.canvas) > y_index \
                       and len(self.canvas[y_index]) > x_index:
                            line.append(self.canvas[y_index][x_index])
                    else:
                        line.append(' ')
                assert len(line) == (smaxcol + 1)
                screen.print_at(''.join(line), 0, y)

            screen.refresh()

            # NOTE: get_event() doesn't block by itself,
            # so we have to do the blocking ourselves.
            #
            # NOTE: using formally private method while waiting for PR [1]
            # to get merged. After that need to adjust asciimatics version
            # requirements.
            #
            # [1] https://github.com/peterbrittain/asciimatics/pull/188
            screen._wait_for_input(self.TIMEOUT)

            event = screen.get_event()
            if not isinstance(event, KeyboardEvent):
                continue

            k = event.key_code
            if k == screen.KEY_DOWN or k == ord('s'):
                offset_y += 1
            elif k == screen.KEY_PAGE_DOWN or k == ord('S'):
                offset_y += smaxrow
            elif k == screen.KEY_UP or k == ord('w'):
                offset_y -= 1
            elif k == screen.KEY_PAGE_UP or k == ord('W'):
                offset_y -= smaxrow
            elif k == screen.KEY_RIGHT or k == ord('d'):
                offset_x += 1
            elif k == ord('D'):
                offset_x += smaxcol
            elif k == screen.KEY_LEFT or k == ord('a'):
                offset_x -= 1
            elif k == ord('A'):
                offset_x -= smaxcol
            elif k == ord('q') or k == ord('Q'):
                break

            if offset_y > max_y:
                offset_y = max_y
            elif offset_y < 0:
                offset_y = 0

            if offset_x > max_x:
                offset_x = max_x
            elif offset_x < 0:
                offset_x = 0