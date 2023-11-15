    def _process_pos(pos, length):
        if pos is None:
            return 0
        return pos + length if pos < 0 else pos