def copy_flow(part, scope, flow, master, state):
    """
    part: _c_ontent, _h_eaders+content, _u_rl
    scope: _a_ll, re_q_uest, re_s_ponse
    """
    data, err = copy_flow_format_data(part, scope, flow)

    if err:
        signals.status_message.send(message=err)
        return

    if not data:
        if scope == "q":
            signals.status_message.send(message="No request content to copy.")
        elif scope == "s":
            signals.status_message.send(message="No response content to copy.")
        else:
            signals.status_message.send(message="No contents to copy.")
        return

    try:
        master.add_event(str(len(data)))
        pyperclip.copy(data)
    except (RuntimeError, UnicodeDecodeError):
        def save(k):
            if k == "y":
                ask_save_path("Save data", data, master, state)
        signals.status_prompt_onekey.send(
            prompt = "Cannot copy binary data to clipboard. Save as file?",
            keys = (
                ("yes", "y"),
                ("no", "n"),
            ),
            callback = save
        )