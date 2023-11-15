    def OnPrevious(self, widget):

        if len(list(self.data.keys())) > 1:

            _list = list(self.data.keys())

            if self.current not in _list:
                ix -= 1  # noqa: F821
            else:
                ix = _list.index(self.current)
                ix -= 1

                if ix < 0:
                    ix = -1
                elif ix >= len(_list):
                    ix = 0

            if ix is not None:
                self.current = _list[ix]

        if self.current is None:
            return

        self.Display(self.current)