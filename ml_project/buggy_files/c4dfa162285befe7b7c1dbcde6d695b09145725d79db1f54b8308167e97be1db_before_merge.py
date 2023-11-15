    def _handler_wrapper(handler: Callable, event_name: Any, event_filter: Callable) -> Callable:
        def wrapper(engine: Engine, *args, **kwargs) -> Any:
            event = engine.state.get_event_attrib_value(event_name)
            if event_filter(engine, event):
                return handler(engine, *args, **kwargs)

        # setup input handler as parent to make has_event_handler work
        wrapper._parent = weakref.ref(handler)
        return wrapper