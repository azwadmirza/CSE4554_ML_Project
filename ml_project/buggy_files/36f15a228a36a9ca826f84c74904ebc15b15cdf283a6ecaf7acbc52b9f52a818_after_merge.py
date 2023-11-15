def drawRightStatus(vd, scr, vs):
    'Draw right side of status bar.  Return length displayed.'
    rightx = vs.windowWidth

    ret = 0
    statcolors = [
        (vd.rightStatus(vs), 'color_status'),
    ]

    active = vs is vd.sheets[0]  # active sheet

    if active:
        statcolors.append((vd.keystrokes or '', 'color_keystrokes'))

    if vs.currentThreads:
        statcolors.insert(0, vd.checkMemoryUsage())
        if vs.progresses:
            gerund = vs.progresses[0].gerund
        else:
            gerund = 'processing'
        statcolors.insert(1, ('  %s %s…' % (vs.progressPct, gerund), 'color_status'))

    if active and vd.currentReplay:
        statcolors.insert(0, (vd.replayStatus, 'color_status_replay'))

    for rstatcolor in statcolors:
        if rstatcolor:
            try:
                rstatus, coloropt = rstatcolor
                rstatus = ' '+rstatus
                cattr = colors.get_color(coloropt)
                if scr is vd.winTop:
                    cattr = update_attr(cattr, colors.color_top_status, 0)
                if active:
                    cattr = update_attr(cattr, colors.color_active_status, 0)
                else:
                    cattr = update_attr(cattr, colors.color_inactive_status, 0)
                statuslen = clipdraw(scr, vs.windowHeight-1, rightx, rstatus, cattr.attr, w=vs.windowWidth-1, rtl=True)
                rightx -= statuslen
                ret += statuslen
            except Exception as e:
                vd.exceptionCaught(e)

    if scr:
        curses.doupdate()
    return ret