def _is_event_name(name):
    return not name.startswith("_") and name != "dispatch"