def match(
        handler: handlers.ResourceHandler,
        cause: causation.ResourceCause,
) -> bool:
    # Kwargs are lazily evaluated on the first _actual_ use, and shared for all filters since then.
    kwargs: MutableMapping[str, Any] = {}
    return all([
        _matches_resource(handler, cause.resource),
        _matches_labels(handler, cause, kwargs),
        _matches_annotations(handler, cause, kwargs),
        _matches_field_values(handler, cause, kwargs),
        _matches_field_changes(handler, cause, kwargs),
        _matches_filter_callback(handler, cause, kwargs),
    ])