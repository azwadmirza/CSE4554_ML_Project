def show_queue():
    """
    Show contents of the mail queue

    CLI Example:

    .. code-block:: bash

        salt '*' postfix.show_queue

    """
    cmd = "mailq"
    out = __salt__["cmd.run"](cmd).splitlines()
    queue = []

    queue_pattern = re.compile(
        r"(?P<queue_id>^[A-Z0-9]+)\s+(?P<size>\d+)\s(?P<timestamp>\w{3}\s\w{3}\s\d{1,2}\s\d{2}\:\d{2}\:\d{2})\s+(?P<sender>.+)"
    )
    recipient_pattern = re.compile(r"^\s+(?P<recipient>.+)")
    queue_id, size, timestamp, sender, recipient = None, None, None, None, None
    for line in out:
        if re.match("^[-|postqueue:|Mail]", line):
            # discard in-queue wrapper
            continue
        if re.match(queue_pattern, line):
            m = re.match(queue_pattern, line)
            queue_id = m.group("queue_id")
            size = m.group("size")
            timestamp = m.group("timestamp")
            sender = m.group("sender")
        elif re.match(recipient_pattern, line):  # recipient/s
            m = re.match(recipient_pattern, line)
            recipient = m.group("recipient")
        elif not line:  # end of record
            if all((queue_id, size, timestamp, sender, recipient)):
                queue.append(
                    {
                        "queue_id": queue_id,
                        "size": size,
                        "timestamp": timestamp,
                        "sender": sender,
                        "recipient": recipient,
                    }
                )
    return queue