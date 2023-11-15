    def beforeExecHook(self, sheet, cmd, args, keystrokes):
        if vd.activeCommand:
            self.afterExecSheet(sheet, False, '')

        colname, rowname, sheetname = '', '', None
        if sheet and not cmd.longname.startswith('open-'):
            sheetname = sheet

            contains = lambda s, *substrs: any((a in s) for a in substrs)
            if contains(cmd.execstr, 'cursorTypedValue', 'cursorDisplay', 'cursorValue', 'cursorCell', 'cursorRow') and sheet.nRows > 0:
                k = sheet.rowkey(sheet.cursorRow)
                rowname = keystr(k) if k else sheet.cursorRowIndex

            if contains(cmd.execstr, 'cursorTypedValue', 'cursorDisplay', 'cursorValue', 'cursorCell', 'cursorCol', 'cursorVisibleCol'):
                colname = sheet.cursorCol.name or sheet.visibleCols.index(sheet.cursorCol)

            if contains(cmd.execstr, 'plotterCursorBox'):
                assert not colname and not rowname
                bb = sheet.cursorBox
                colname = '%s %s' % (sheet.formatX(bb.xmin), sheet.formatX(bb.xmax))
                rowname = '%s %s' % (sheet.formatY(bb.ymin), sheet.formatY(bb.ymax))
            elif contains(cmd.execstr, 'plotterVisibleBox'):
                assert not colname and not rowname
                bb = sheet.visibleBox
                colname = '%s %s' % (sheet.formatX(bb.xmin), sheet.formatX(bb.xmax))
                rowname = '%s %s' % (sheet.formatY(bb.ymin), sheet.formatY(bb.ymax))


        comment = vd.currentReplayRow.comment if vd.currentReplayRow else cmd.helpstr
        vd.activeCommand = self.newRow(sheet=sheetname,
                                            col=str(colname),
                                            row=str(rowname),
                                            keystrokes=keystrokes,
                                            input=args,
                                            longname=cmd.longname,
                                            comment=comment,
                                            undofuncs=[])