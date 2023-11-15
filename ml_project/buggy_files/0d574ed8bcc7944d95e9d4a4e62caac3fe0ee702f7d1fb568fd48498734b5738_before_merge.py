def configuredcommands_rclick(c,p,menu):
    """ Provide "edit in EDITOR" context menu item """
    config = c.config.getData('contextmenu_commands')
    if config:
        cmds = [el.split(None,1) for el in config]
        for cmd, desc in cmds:
            desc = desc.strip()
            action = menu.addAction(desc)
            #action.setToolTip(cmd)
            def create_callback(cm):
                return lambda: c.k.simulateCommand(cm)
            configcmd_rclick_cb = create_callback(cmd)
            action.triggered.connect(configcmd_rclick_cb)