def _fetch_reference_injections(
        fn: Callable[..., Any],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    # # Hotfix, see: https://github.com/ets-labs/python-dependency-injector/issues/362
    if GenericAlias and fn is GenericAlias:
        fn = fn.__init__

    signature = inspect.signature(fn)

    injections = {}
    closing = {}
    for parameter_name, parameter in signature.parameters.items():
        if not isinstance(parameter.default, _Marker) \
                and not _is_fastapi_depends(parameter.default):
            continue

        marker = parameter.default

        if _is_fastapi_depends(marker):
            marker = marker.dependency

            if not isinstance(marker, _Marker):
                continue

        if isinstance(marker, Closing):
            marker = marker.provider
            closing[parameter_name] = marker

        injections[parameter_name] = marker
    return injections, closing