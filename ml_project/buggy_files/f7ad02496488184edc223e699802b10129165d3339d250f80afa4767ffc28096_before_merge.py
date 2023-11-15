def track_creator(player, position=None, other_track=None):
    if position == "np":
        queued_track = player.current
    elif position is None:
        queued_track = other_track
    else:
        queued_track = player.queue[position]
    track_keys = queued_track._info.keys()
    track_values = queued_track._info.values()
    track_id = queued_track.track_identifier
    track_info = {}
    for k, v in zip(track_keys, track_values):
        track_info[k] = v
    keys = ["track", "info"]
    values = [track_id, track_info]
    track_obj = {}
    for key, value in zip(keys, values):
        track_obj[key] = value
    return track_obj