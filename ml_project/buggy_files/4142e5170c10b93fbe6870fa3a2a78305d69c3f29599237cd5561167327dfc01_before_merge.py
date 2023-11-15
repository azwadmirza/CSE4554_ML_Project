async def match_event(event, event_opts):
    """Filter and matches the event."""
    event_type = event_opts.get("type", None)

    if event_type:
        # The event type can be specified with a string
        if isinstance(event_type, str):
            # pylint: disable=invalid-name
            et = Event.event_registry.get(event_type, None)
            if et is None:
                raise ValueError(
                    "{event_type} is not a valid opsdroid"
                    " event representation.".format(event_type=event_type)
                )
            event_type = et

        # TODO: Add option to match all subclasses as well
        # if isinstance(event, event_type):
        # pylint: disable=unidiomatic-typecheck
        if type(event) is event_type:
            for key in event_opts:
                if key != "type":
                    event_value = event_opts.get(key, None)
                    entity_value = event.entities.get(key, {}).get("value", None)

                    if event_value != entity_value:
                        return False

            return True

    return False