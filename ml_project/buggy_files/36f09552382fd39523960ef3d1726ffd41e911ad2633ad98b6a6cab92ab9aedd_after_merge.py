async def queue_duration(ctx) -> int:
    player = lavalink.get_player(ctx.guild.id)
    duration = []
    for i in range(len(player.queue)):
        if not player.queue[i].is_stream:
            duration.append(player.queue[i].length)
    queue_dur = sum(duration)
    if not player.queue:
        queue_dur = 0
    try:
        if not player.current.is_stream:
            remain = player.current.length - player.position
        else:
            remain = 0
    except AttributeError:
        remain = 0
    queue_total_duration = remain + queue_dur
    return queue_total_duration