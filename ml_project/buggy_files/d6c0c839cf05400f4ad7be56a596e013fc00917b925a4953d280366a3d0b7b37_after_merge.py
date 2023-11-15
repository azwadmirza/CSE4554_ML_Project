    def update_frame(self, key, ranges=None, element=None):
        """
        Update the internal state of the Plot to represent the given
        key tuple (where integers represent frames). Returns this
        state.
        """
        reused = isinstance(self.hmap, DynamicMap) and self.overlaid
        if not reused and element is None:
            element = self._get_frame(key)
        elif element is not None:
            self.current_frame = element
            self.current_key = key
        items = element.items() if element else []

        if isinstance(self.hmap, DynamicMap):
            range_obj = element
        else:
            range_obj = self.hmap

        if element is not None:
            ranges = self.compute_ranges(range_obj, key, ranges)

        if element and not self.overlaid and not self.tabs and not self.batched:
            self._update_ranges(element, ranges)

        # Determine which stream (if any) triggered the update
        triggering = [stream for stream in self.streams if stream._triggering]

        for k, subplot in self.subplots.items():
            el = None

            # If in Dynamic mode propagate elements to subplots
            if isinstance(self.hmap, DynamicMap) and element:
                # In batched mode NdOverlay is passed to subplot directly
                if self.batched:
                    el = element
                # If not batched get the Element matching the subplot
                elif element is not None:
                    idx, spec, exact = dynamic_update(self, subplot, k, element, items)
                    if idx is not None:
                        _, el = items.pop(idx)
                        if not exact:
                            self._update_subplot(subplot, spec)

                # Skip updates to subplots when its streams is not one of
                # the streams that initiated the update
                if triggering and all(s not in triggering for s in subplot.streams):
                    continue
            subplot.update_frame(key, ranges, element=el)

        if not self.batched and isinstance(self.hmap, DynamicMap) and items:
            init_kwargs = {'plots': self.handles['plots']}
            if not self.tabs:
                init_kwargs['plot'] = self.handles['plot']
            self._create_dynamic_subplots(key, items, ranges, **init_kwargs)
            if not self.overlaid and not self.tabs:
                self._process_legend()

        if element and not self.overlaid and not self.tabs and not self.batched:
            self._update_plot(key, self.handles['plot'], element)

        self._execute_hooks(element)