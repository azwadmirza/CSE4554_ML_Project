    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self.check_position_caller)
        self.register_event_type("on_dismiss")
        self.register_event_type("on_enter")
        self.register_event_type("on_leave")
        self.menu = self.ids.md_menu
        self.target_height = 0