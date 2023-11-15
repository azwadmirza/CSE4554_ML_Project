    def create_application(self, full_layout=True):
        """ makes the application object and the buffers """
        layout_manager = LayoutManager(self)
        if full_layout:
            layout = layout_manager.create_layout(ExampleLexer, ToolbarLexer)
        else:
            layout = layout_manager.create_tutorial_layout()

        buffers = {
            DEFAULT_BUFFER: Buffer(is_multiline=True),
            'description': Buffer(is_multiline=True, read_only=True),
            'parameter': Buffer(is_multiline=True, read_only=True),
            'examples': Buffer(is_multiline=True, read_only=True),
            'bottom_toolbar': Buffer(is_multiline=True),
            'example_line': Buffer(is_multiline=True),
            'default_values': Buffer(),
            'symbols': Buffer(),
            'progress': Buffer(is_multiline=False)
        }

        writing_buffer = Buffer(
            history=self.history,
            auto_suggest=AutoSuggestFromHistory(),
            enable_history_search=True,
            completer=self.completer,
            complete_while_typing=Always()
        )

        return Application(
            mouse_support=False,
            style=self.styles,
            buffer=writing_buffer,
            on_input_timeout=self.on_input_timeout,
            key_bindings_registry=InteractiveKeyBindings(self).registry,
            layout=layout,
            buffers=buffers,
        )