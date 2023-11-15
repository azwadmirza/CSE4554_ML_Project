def track_creator(player, position=None, other_track=None) -> MutableMapping:
    if position == "np":
        queued_track = player.current
    elif position is None:
        queued_track = other_track
    else:
        queued_track = player.queue[position]
    return track_to_json(queued_track)