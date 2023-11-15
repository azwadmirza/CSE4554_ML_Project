    def _init_glyph(self, plot, mapping, properties, key):
        """
        Returns a Bokeh glyph object.
        """
        properties = {k: v for k, v in properties.items() if 'legend' not in k}

        if key == 'arrow_1':
            source = properties.pop('source')
            arrow_end = mapping.pop('arrow_end')
            arrow_start = mapping.pop('arrow_start')
            for p in ('alpha', 'color'):
                v = properties.pop(p, None)
                for t in ('line', 'fill'):
                    if v is None:
                        continue
                    key = '_'.join([t, p])
                    if key not in properties:
                        properties[key] = v
            start = arrow_start(**properties) if arrow_start else None
            end = arrow_end(**properties) if arrow_end else None
            line_props = {p: v for p, v in properties.items() if p.startswith('line_')}
            renderer = Arrow(start=start, end=end, source=source,
                             **dict(line_props, **mapping))
            glyph = renderer
        else:
            properties = {p if p == 'source' else 'text_'+p: v
                          for p, v in properties.items()}
            renderer, glyph = super(ArrowPlot, self)._init_glyph(
                plot, mapping, properties, key)
        plot.renderers.append(renderer)
        return renderer, glyph