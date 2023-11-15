def _warn_if_text_is_missing(endpoint: str, kwargs: Dict[str, Any]) -> None:
    attachments = kwargs.get("attachments")
    if attachments and isinstance(attachments, list):
        if all(
            [
                attachment.get("fallback")
                and len(attachment.get("fallback").strip()) != 0
                for attachment in attachments
            ]
        ):
            return
        missing = "fallback"
    else:
        text = kwargs.get("text")
        if text and len(text.strip()) != 0:
            return
        missing = "text"
    message = (
        f"The `{missing}` argument is missing in the request payload for a {endpoint} call - "
        f"It's a best practice to always provide a `{missing}` argument when posting a message. "
        f"The `{missing}` argument is used in places where content cannot be rendered such as: "
        "system push notifications, assistive technology such as screen readers, etc."
    )
    # for unit tests etc.
    skip_deprecation = os.environ.get("SKIP_SLACK_SDK_WARNING")
    if skip_deprecation:
        return
    warnings.warn(message, UserWarning)