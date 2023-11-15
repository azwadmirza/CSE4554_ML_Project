def ask_save_body(scope, flow):
    """
    Save either the request or the response body to disk.

    scope: re_q_uest, re_s_ponse, _b_oth, None (ask user if necessary)
    """

    request_has_content = flow.request and flow.request.raw_content
    response_has_content = flow.response and flow.response.raw_content

    if scope is None:
        ask_scope_and_callback(flow, ask_save_body)
    elif scope == "q" and request_has_content:
        ask_save_path(
            flow.request.get_content(strict=False),
            "Save request content to"
        )
    elif scope == "s" and response_has_content:
        ask_save_path(
            flow.response.get_content(strict=False),
            "Save response content to"
        )
    elif scope == "b" and request_has_content and response_has_content:
        ask_save_path(
            (flow.request.get_content(strict=False) + b"\n" +
             flow.response.get_content(strict=False)),
            "Save request & response content to"
        )
    else:
        signals.status_message.send(message="No content.")