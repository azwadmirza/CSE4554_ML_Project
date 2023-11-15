def afterExecSheet(cmdlog, sheet, escaped, err):
    if vd.macroMode and (vd.activeCommand is not None) and (vd.activeCommand is not UNLOADED):
        cmd = copy(vd.activeCommand)
        cmd.row = cmd.col = cmd.sheet = ''
        vd.macroMode.addRow(cmd)

    # the following needs to happen at the end, bc
    # once cmdlog.afterExecSheet.__wrapped__ runs, vd.activeCommand resets to None
    cmdlog.afterExecSheet.__wrapped__(cmdlog, sheet, escaped, err)