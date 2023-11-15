def print_output_event(event, stream, is_terminal):
    if 'errorDetail' in event:
        raise StreamOutputError(event['errorDetail']['message'])

    terminator = ''

    if is_terminal and 'stream' not in event:
        # erase current line
        write_to_stream("%c[2K\r" % 27, stream)
        terminator = "\r"
    elif 'progressDetail' in event:
        return

    if 'time' in event:
        write_to_stream("[%s] " % event['time'], stream)

    if 'id' in event:
        write_to_stream("%s: " % event['id'], stream)

    if 'from' in event:
        write_to_stream("(from %s) " % event['from'], stream)

    status = event.get('status', '')

    if 'progress' in event:
        write_to_stream("%s %s%s" % (status, event['progress'], terminator), stream)
    elif 'progressDetail' in event:
        detail = event['progressDetail']
        total = detail.get('total')
        if 'current' in detail and total:
            percentage = float(detail['current']) / float(total) * 100
            write_to_stream('%s (%.1f%%)%s' % (status, percentage, terminator), stream)
        else:
            write_to_stream('%s%s' % (status, terminator), stream)
    elif 'stream' in event:
        write_to_stream("%s%s" % (event['stream'], terminator), stream)
    else:
        write_to_stream("%s%s\n" % (status, terminator), stream)