        def wrapper(*args, **kwargs) -> Any:
            event = self.state.get_event_attrib_value(event_name)
            if event_filter(self, event):
                return handler(*args, **kwargs)