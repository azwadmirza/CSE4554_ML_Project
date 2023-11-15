    def text(self, x, y, s, *args, **kwargs):
        """
        Add text to figure.

        Call signature::

          text(x, y, s, fontdict=None, **kwargs)

        Add text to figure at location *x*, *y* (relative 0-1
        coords). See :func:`~matplotlib.pyplot.text` for the meaning
        of the other arguments.

        kwargs control the :class:`~matplotlib.text.Text` properties:

        %(Text)s
        """

        override = _process_text_args({}, *args, **kwargs)
        t = Text(x=x, y=y, text=s)

        t.update(override)
        self._set_artist_props(t)
        self.texts.append(t)
        t._remove_method = lambda h: self.texts.remove(h)
        return t