def set_x(sheet, s):
    xmin, xmax = map(float, map(sheet.xcols[0].type, s.split()))
    sheet.zoomTo(BoundingBox(xmin, sheet.visibleBox.ymin, xmax, sheet.visibleBox.ymax))
    sheet.refresh()