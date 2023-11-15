def _is_event_name(name):
    # _sa_event prefix is special to support internal-only event names.
    # most event names are just plain method names that aren't
    # underscored.

    return (
        not name.startswith("_") and name != "dispatch"
    ) or name.startswith("_sa_event")