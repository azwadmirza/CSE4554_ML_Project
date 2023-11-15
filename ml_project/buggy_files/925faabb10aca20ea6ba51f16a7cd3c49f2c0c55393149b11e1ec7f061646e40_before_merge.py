def setMacro(ks, vs):
    vd.macrobindings[ks] = vs
    BaseSheet.addCommand(ks, vs.name, 'runMacro(vd.macrobindings[keystrokes])')