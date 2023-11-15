def stream_output(output, stream):
    is_terminal = hasattr(stream, 'isatty') and stream.isatty()
    stream = utils.get_output_stream(stream)
    all_events = []
    lines = {}
    diff = 0

    for event in utils.json_stream(output):
        all_events.append(event)
        is_progress_event = 'progress' in event or 'progressDetail' in event

        if not is_progress_event:
            print_output_event(event, stream, is_terminal)
            stream.flush()
            continue

        if not is_terminal:
            continue

        # if it's a progress event and we have a terminal, then display the progress bars
        image_id = event.get('id')
        if not image_id:
            continue

        if image_id not in lines:
            lines[image_id] = len(lines)
            write_to_stream("\n", stream)

        diff = len(lines) - lines[image_id]

        # move cursor up `diff` rows
        write_to_stream("%c[%dA" % (27, diff), stream)

        print_output_event(event, stream, is_terminal)

        if 'id' in event:
            # move cursor back down
            write_to_stream("%c[%dB" % (27, diff), stream)

        stream.flush()

    return all_events