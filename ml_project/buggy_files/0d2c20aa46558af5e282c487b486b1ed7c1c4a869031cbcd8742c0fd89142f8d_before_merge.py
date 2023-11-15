    def getPreviousSettings(self, fn):
        '''
        Return the settings in effect for fn. Typically, this involves
        pre-reading fn.
        '''
        lm = self
        settingsName = 'settings dict for %s' % g.shortFileName(fn)
        shortcutsName = 'shortcuts dict for %s' % g.shortFileName(fn)
        # A special case: settings in leoSettings.leo do *not* override
        # the global settings, that is, settings in myLeoSettings.leo.
        isLeoSettings = g.shortFileName(fn).lower() == 'leosettings.leo'
        exists = g.os_path_exists(fn)
        if fn and exists and lm.isLeoFile(fn) and not isLeoSettings:
            # Open the file usinging a null gui.
            try:
                g.app.preReadFlag = True
                c = lm.openSettingsFile(fn)
            finally:
                g.app.preReadFlag = False
            # Merge the settings from c into *copies* of the global dicts.
            d1, d2 = lm.computeLocalSettings(c,
                lm.globalSettingsDict, lm.globalBindingsDict, localFlag=True)
                    # d1 and d2 are copies.
            d1.setName(settingsName)
            d2.setName(shortcutsName)
        else:
            # Get the settings from the globals settings dicts.
            d1 = lm.globalSettingsDict.copy(settingsName)
            d2 = lm.globalBindingsDict.copy(shortcutsName)
        return PreviousSettings(d1, d2)