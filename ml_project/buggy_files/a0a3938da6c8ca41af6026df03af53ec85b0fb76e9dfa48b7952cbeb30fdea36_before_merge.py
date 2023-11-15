def afterExecSheet(cmdlog, sheet, escaped, err):
    cmdlog.afterExecSheet.__wrapped__(cmdlog, sheet, escaped, err)
    if vd.macroMode and (vd.activeCommand is not None) and (vd.activeCommand is not UNLOADED):
        cmd = copy(vd.activeCommand)
        cmd.row = cmd.col = cmd.sheet = ''
        vd.macroMode.addRow(cmd)