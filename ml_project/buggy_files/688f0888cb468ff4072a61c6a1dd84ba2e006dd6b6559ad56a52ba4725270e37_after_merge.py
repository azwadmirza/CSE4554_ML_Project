    def moveto(self, n):
        self.fp.write(_unicode('\n' * n + _term_move_up() * -n))