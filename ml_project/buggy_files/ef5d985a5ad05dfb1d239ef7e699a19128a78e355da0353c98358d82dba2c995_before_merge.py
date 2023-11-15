    def _init_tools(self, element, callbacks=[]):
        """
        Processes the list of tools to be supplied to the plot.
        """
        tooltips, hover_opts = self._hover_opts(element)
        tooltips = [(ttp.pprint_label, '@{%s}' % util.dimension_sanitizer(ttp.name))
                    if isinstance(ttp, Dimension) else ttp for ttp in tooltips]
        if not tooltips: tooltips = None

        callbacks = callbacks+self.callbacks
        cb_tools, tool_names = [], []
        hover = False
        for cb in callbacks:
            for handle in cb.models+cb.extra_models:
                if handle and handle in known_tools:
                    tool_names.append(handle)
                    if handle == 'hover':
                        tool = HoverTool(tooltips=tooltips, **hover_opts)
                        hover = tool
                    else:
                        tool = known_tools[handle]()
                    cb_tools.append(tool)
                    self.handles[handle] = tool

        tools = [t for t in cb_tools + self.default_tools + self.tools
                 if t not in tool_names]
        hover_tools = [t for t in tools if isinstance(t, HoverTool)]
        if 'hover' in tools:
            hover = HoverTool(tooltips=tooltips, **hover_opts)
            tools[tools.index('hover')] = hover
        elif any(hover_tools):
            hover = hover_tools[0]
        if hover:
            self.handles['hover'] = hover
        return tools