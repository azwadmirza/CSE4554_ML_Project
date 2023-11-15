def set_x(sheet, s):
    xmin, xmax = map(float, map(sheet.parseX, s.split()))
    sheet.zoomTo(BoundingBox(xmin, sheet.visibleBox.ymin, xmax, sheet.visibleBox.ymax))
    sheet.refresh()