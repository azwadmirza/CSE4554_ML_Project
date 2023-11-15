def collect_paths_events(report, file_ids):
    files = file_ids.keys()

    bug_paths = []
    bug_events = []

    events = filter(lambda i: i.get('kind') == 'event', report.bug_path)

    # Create remaining data for bugs and send them to the server.  In plist
    # file the source and target of the arrows are provided as starting and
    # ending ranges of the arrow. The path A->B->C is given as A->B and
    # B->C, thus range B is provided twice. So in the loop only target
    # points of the arrows are stored, and an extra insertion is done for
    # the source of the first arrow before the loop.
    report_path = filter(lambda i: i.get('kind') == 'control',
                         report.bug_path)

    if report_path:
        start_range = report_path[0]['edges'][0]['start']
        start1_line = start_range[0]['line']
        start1_col = start_range[0]['col']
        start2_line = start_range[1]['line']
        start2_col = start_range[1]['col']
        source_file_path = files[start_range[1]['file']]
        bug_paths.append(shared.ttypes.BugPathPos(
            start1_line,
            start1_col,
            start2_line,
            start2_col,
            file_ids[source_file_path]))

    for path in report_path:
        try:
            end_range = path['edges'][0]['end']
            end1_line = end_range[0]['line']
            end1_col = end_range[0]['col']
            end2_line = end_range[1]['line']
            end2_col = end_range[1]['col']
            source_file_path = files[end_range[1]['file']]
            bug_paths.append(shared.ttypes.BugPathPos(
                end1_line,
                end1_col,
                end2_line,
                end2_col,
                file_ids[source_file_path]))
        except IndexError:
            # Edges might be empty nothing can be stored.
            continue

    for event in events:
        file_path = files[event['location']['file']]
        bug_events.append(shared.ttypes.BugPathEvent(
            event['location']['line'],
            event['location']['col'],
            event['location']['line'],
            event['location']['col'],
            event['message'],
            file_ids[file_path]))

    return bug_paths, bug_events