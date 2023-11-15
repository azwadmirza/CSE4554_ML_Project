    def __call__(self, event_filter: Optional[Callable] = None,
                 every: Optional[int] = None, once: Optional[int] = None) -> Union[CallableEvents, EventWithFilter]:

        if not ((event_filter is not None) ^ (every is not None) ^ (once is not None)):
            raise ValueError("Only one of the input arguments should be specified")

        if (event_filter is not None) and not callable(event_filter):
            raise TypeError("Argument event_filter should be a callable")

        if (every is not None) and not (isinstance(every, numbers.Integral) and every > 0):
            raise ValueError("Argument every should be integer and greater than zero")

        if (once is not None) and not (isinstance(once, numbers.Integral) and once > 0):
            raise ValueError("Argument every should be integer and positive")

        if every is not None:
            if every == 1:
                # Just return the event itself
                return self
            event_filter = CallableEvents.every_event_filter(every)

        if once is not None:
            event_filter = CallableEvents.once_event_filter(once)

        # check signature:
        _check_signature("engine", event_filter, "event_filter", "event")

        return EventWithFilter(self, event_filter)