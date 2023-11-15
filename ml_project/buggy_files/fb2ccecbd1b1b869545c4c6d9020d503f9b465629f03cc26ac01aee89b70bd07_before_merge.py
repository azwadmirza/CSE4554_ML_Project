    def copy_to_my_settings(self, unl, which):
        """copy_to_my_settings - copy setting from leoSettings.leo

        :param str unl: Leo UNL to copy from
        :param int which: 1-3, leaf, leaf's parent, leaf's grandparent
        :return: unl of leaf copy in myLeoSettings.leo
        :rtype: str
        """
        trace = False and not g.unitTesting
        if trace: g.es(unl)
        path, unl = unl.split('#', 1)
        # Undo the replacements made in p.getUNL.
        path = path.replace("file://", "")
        unl = unl.replace('%20', ' ').split("-->")
        tail = []
        if which > 1: # copying parent or grandparent but select leaf later
            tail = unl[-(which - 1):]
        unl = unl[: len(unl) + 1 - which]
        my_settings_c = self.c.openMyLeoSettings()
        my_settings_c.save() # if it didn't exist before, save required
        settings = g.findNodeAnywhere(my_settings_c, '@settings')
        c2 = g.app.loadManager.openSettingsFile(path)
        found, maxdepth, maxp = g.recursiveUNLFind(unl, c2)
        if found:
            if trace: g.trace('FOUND', unl)
            dest = maxp.get_UNL()
        else:
            if trace: g.trace('CREATING', unl)
            nd = settings.insertAsLastChild()
            dest = nd.get_UNL()
            self.copy_recursively(maxp, nd)
            my_settings_c.redraw()
            shortcutsDict, settingsDict = g.app.loadManager.createSettingsDicts(my_settings_c, False)
            self.c.config.settingsDict.update(settingsDict)
            my_settings_c.config.settingsDict.update(settingsDict)
        if trace: g.trace('-->'.join([dest] + tail))
        return '-->'.join([dest] + tail)