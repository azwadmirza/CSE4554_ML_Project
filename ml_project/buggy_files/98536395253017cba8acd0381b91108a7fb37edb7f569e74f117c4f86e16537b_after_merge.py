    def _process_pos(pos, length, is_start):
        if pos is None:
            return 0 if is_start else length
        return pos + length if pos < 0 else pos