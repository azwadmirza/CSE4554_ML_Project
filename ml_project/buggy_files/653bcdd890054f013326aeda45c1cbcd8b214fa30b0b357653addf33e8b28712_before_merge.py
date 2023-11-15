def _get_most_recent_snapshot(snapshots, max_snapshot_age_secs=None, now=None):
    """
    Gets the most recently created snapshot and optionally filters the result
    if the snapshot is too old
    :param snapshots: list of snapshots to search
    :param max_snapshot_age_secs: filter the result if its older than this
    :param now: simulate time -- used for unit testing
    :return:
    """
    if len(snapshots) == 0:
        return None

    if not now:
        now = datetime.datetime.utcnow()

    youngest_snapshot = max(snapshots, key=_get_snapshot_starttime)

    # See if the snapshot is younger that the given max age
    snapshot_start = datetime.datetime.strptime(youngest_snapshot.start_time, '%Y-%m-%dT%H:%M:%S.000Z')
    snapshot_age = now - snapshot_start

    if max_snapshot_age_secs is not None:
        if snapshot_age.total_seconds() > max_snapshot_age_secs:
            return None

    return youngest_snapshot