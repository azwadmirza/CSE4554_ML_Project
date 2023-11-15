async def draw_time(ctx) -> str:
    player = lavalink.get_player(ctx.guild.id)
    paused = player.paused
    pos = player.position
    dur = player.current.length
    sections = 12
    loc_time = round((pos / dur) * sections)
    bar = "\N{BOX DRAWINGS HEAVY HORIZONTAL}"
    seek = "\N{RADIO BUTTON}"
    if paused:
        msg = "\N{DOUBLE VERTICAL BAR}"
    else:
        msg = "\N{BLACK RIGHT-POINTING TRIANGLE}"
    for i in range(sections):
        if i == loc_time:
            msg += seek
        else:
            msg += bar
    return msg