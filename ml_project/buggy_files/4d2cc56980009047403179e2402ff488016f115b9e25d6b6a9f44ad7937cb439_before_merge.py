    def __str__(self):
        with pretty():
            c = colored.yellow
            lines = ['' + c("<HyCons (")]
            while True:
                lines.append("  " + repr_indent(self.car))
                if not isinstance(self.cdr, HyCons):
                    break
                self = self.cdr
            lines.append("{} {}{}".format(
                c("."), repr_indent(self.cdr), c(")>")))
            return '\n'.join(lines)