def _get_server_start_message(is_ipv6_message: bool = False) -> Tuple[str, str]:
    if is_ipv6_message:
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