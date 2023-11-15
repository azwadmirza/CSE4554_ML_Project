    def __str__(self):
        with pretty():
            g = colored.green
            if self:
                pairs = []
                for k, v in zip(self[::2],self[1::2]):
                    k, v = repr_indent(k), repr_indent(v)
                    pairs.append(
                        ("{0}{c}\n  {1}\n  "
                         if '\n' in k+v
                         else "{0}{c} {1}").format(k, v, c=g(',')))
                if len(self) % 2 == 1:
                    pairs.append("{}  {}\n".format(
                        repr_indent(self[-1]), g("# odd")))
                return "{}\n  {}{}".format(
                    g("HyDict(["), ("{c}\n  ".format(c=g(',')).join(pairs)), g("])"))
            else:
                return '' + g("HyDict()")