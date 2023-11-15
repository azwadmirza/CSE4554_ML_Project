def set_y(sheet, s):
    ymin, ymax = map(float, map(sheet.ycols[0].type, s.split()))
    sheet.zoomTo(BoundingBox(sheet.visibleBox.xmin, ymin, sheet.visibleBox.xmax, ymax))
    sheet.refresh()