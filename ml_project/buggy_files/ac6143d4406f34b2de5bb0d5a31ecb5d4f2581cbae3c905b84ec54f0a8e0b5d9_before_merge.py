    def computeThemeFilePath(self):
        '''Return the absolute path to the theme .leo file.'''
        lm = self
        resolve = self.resolve_theme_path
        # Step 1: Use the --theme file if it exists
        path = resolve(lm.options.get('theme_path'), tag='--theme')
        if path: return path
        # Step 2: look for the @string theme-name setting in the first loaded file.
        # This is a hack, but especially useful for test*.leo files in leo/themes.
        path = lm.files and lm.files[0]
        if path and g.os_path_exists(path):
            # Tricky: we must call lm.computeLocalSettings *here*.
            theme_c = lm.openSettingsFile(path)
            if not theme_c:
                return None # Fix #843.
            settings_d, junk_shortcuts_d = lm.computeLocalSettings(
                c=theme_c,
                settings_d=lm.globalSettingsDict,
                bindings_d=lm.globalBindingsDict,
                localFlag=False,
            )
            setting = settings_d.get_string_setting('theme-name')
            if setting:
                tag = theme_c.shortFileName()
                path = resolve(setting, tag=tag)
                if path: return path
        # Finally, use the setting in myLeoSettings.leo.
        setting = lm.globalSettingsDict.get_string_setting('theme-name')
        tag = 'myLeoSettings.leo'
        return resolve(setting, tag=tag)