def _get_server_start_message(
    host_ip_version: _IPKind = _IPKind.IPv4,
) -> Tuple[str, str]:
    if host_ip_version is _IPKind.IPv6:
        ip_repr = "%s://[%s]:%d"
    else:
        ip_repr = "%s://%s:%d"
    message = f"Uvicorn running on {ip_repr} (Press CTRL+C to quit)"
    color_message = (
        "Uvicorn running on "
        + click.style(ip_repr, bold=True)
        + " (Press CTRL+C to quit)"
    )
    return message, color_message