        def wrapper(engine: Engine, *args, **kwargs) -> Any:
            event = engine.state.get_event_attrib_value(event_name)
            if event_filter(engine, event):
                return handler(engine, *args, **kwargs)