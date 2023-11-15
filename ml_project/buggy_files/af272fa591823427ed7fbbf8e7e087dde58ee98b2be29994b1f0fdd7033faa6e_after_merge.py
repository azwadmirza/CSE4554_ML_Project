def match(
        handler: handlers.ResourceHandler,
        cause: causation.ResourceCause,
) -> bool:
    # Kwargs are lazily evaluated on the first _actual_ use, and shared for all filters since then.
    kwargs: MutableMapping[str, Any] = {}
    return (
        _matches_resource(handler, cause.resource) and
        _matches_labels(handler, cause, kwargs) and
        _matches_annotations(handler, cause, kwargs) and
        _matches_field_values(handler, cause, kwargs) and
        _matches_field_changes(handler, cause, kwargs) and
        _matches_filter_callback(handler, cause, kwargs)  # the callback comes in the end!
    )