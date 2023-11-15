def getMouseDelta(nsevent):
    dx = nsevent.deltaX()
    dy = -nsevent.deltaY()
    return int(round(dx)), int(round(dy))