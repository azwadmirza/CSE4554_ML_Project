    def update_frame(self, key, ranges=None, plot=None, element=None):
        """
        Updates an existing plot with data corresponding
        to the key.
        """
        reused = isinstance(self.hmap, DynamicMap) and (self.overlaid or self.batched)
        if not reused and element is None:
            element = self._get_frame(key)
        elif element is not None:
            self.current_key = key
            self.current_frame = element

        renderer = self.handles.get('glyph_renderer', None)
        glyph = self.handles.get('glyph', None)
        visible = element is not None
        if hasattr(renderer, 'visible'):
            renderer.visible = visible
        if hasattr(glyph, 'visible'):
            glyph.visible = visible

        if ((self.batched and not element) or element is None or (not self.dynamic and self.static) or
            (self.streaming and self.streaming[0].data is self.current_frame.data and not self.streaming[0]._triggering)):
            return

        if self.batched:
            style_element = element.last
            max_cycles = None
        else:
            style_element = element
            max_cycles = len(self.style._options)
        style = self.lookup_options(style_element, 'style')
        self.style = style.max_cycles(max_cycles) if max_cycles else style

        ranges = self.compute_ranges(self.hmap, key, ranges)
        self.set_param(**self.lookup_options(style_element, 'plot').options)
        ranges = util.match_spec(style_element, ranges)
        self.current_ranges = ranges
        plot = self.handles['plot']
        if not self.overlaid:
            self._update_ranges(style_element, ranges)
            self._update_plot(key, plot, style_element)

        self._update_glyphs(element, ranges)
        self._execute_hooks(element)