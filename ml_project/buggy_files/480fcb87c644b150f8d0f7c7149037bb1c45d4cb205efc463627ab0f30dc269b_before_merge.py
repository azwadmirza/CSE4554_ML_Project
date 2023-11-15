    def _merge_tools(self, subplot):
        """
        Merges tools on the overlay with those on the subplots.
        """
        if self.batched and 'hover' in subplot.handles:
            self.handles['hover'] = subplot.handles['hover']
        elif 'hover' in subplot.handles and 'hover_tools' in self.handles:
            hover = subplot.handles['hover']
            # Datetime formatter may have been applied, remove _dt_strings
            # to match on the hover tooltips, then merge tool renderers
            if hover.tooltips:
                tooltips = tuple((name, spec.replace('_dt_strings', ''))
                                  for name, spec in hover.tooltips)
            else:
                tooltips = ()
            tool = self.handles['hover_tools'].get(tooltips)
            if tool:
                tool_renderers = [] if tool.renderers == 'auto' else tool.renderers
                hover_renderers = [] if hover.renderers == 'auto' else hover.renderers
                renderers = tool_renderers + hover_renderers
                tool.renderers = list(util.unique_iterator(renderers))
            if 'hover' not in self.handles:
                self.handles['hover'] = tool