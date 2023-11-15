    def createSettingsDicts(self, c, localFlag, theme=False):
        import leo.core.leoConfig as leoConfig
        if c:
            parser = leoConfig.SettingsTreeParser(c, localFlag)
                # returns the *raw* shortcutsDict, not a *merged* shortcuts dict.
            shortcutsDict, settingsDict = parser.traverse(theme=theme)
            return shortcutsDict, settingsDict
        return None, None