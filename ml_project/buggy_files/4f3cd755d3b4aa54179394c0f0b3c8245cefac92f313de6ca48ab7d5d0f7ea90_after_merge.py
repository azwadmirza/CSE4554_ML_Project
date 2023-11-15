    def draw_annotation(self, axis, data, opts):
        x, y, text, direction, points, arrowstyle = data
        if self.invert_axes: x, y = y, x
        direction = direction.lower()
        arrowprops = dict({'arrowstyle':arrowstyle},
                          **{k: opts[k] for k in self._arrow_style_opts if k in opts})
        textopts = {k: opts[k] for k in self._text_style_opts if k in opts}
        if direction in ['v', '^']:
            xytext = (0, points if direction=='v' else -points)
        elif direction in ['>', '<']:
            xytext = (points if direction=='<' else -points, 0)
        if 'textsize' in textopts:
            textopts['fontsize'] = textopts.pop('textsize')
        return [axis.annotate(text, xy=(x, y), textcoords='offset points',
                              xytext=xytext, ha="center", va="center",
                              arrowprops=arrowprops, **textopts)]