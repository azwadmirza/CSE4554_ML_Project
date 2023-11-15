    def applyPrefs(self):
        """Write preferences to the current configuration."""
        if not self.proPrefs.isModified():
            return

        if platform.system() == 'Darwin':
            re_cmd2ctrl = re.compile('^Cmd\+', re.I)

        for sectionName in self.prefsSpec:
            for prefName in self.prefsSpec[sectionName]:
                if prefName in ['version']:  # any other prefs not to show?
                    continue

                thisPref = self.proPrefs.getPrefVal(sectionName, prefName)
                # handle special cases
                if prefName in ('codeFont', 'commentFont', 'outputFont'):
                    self.prefsCfg[sectionName][prefName] = \
                        self.fontList[thisPref]
                    continue
                if prefName in ('theme',):
                    self.prefsCfg[sectionName][prefName] = \
                        self.themeList[thisPref]
                    continue
                elif prefName == 'audioDevice':
                    self.prefsCfg[sectionName][prefName] = \
                        self.audioDevNames[thisPref]
                    continue
                elif prefName == 'locale':
                    # '' corresponds to system locale
                    locales = [''] + self.app.localization.available
                    self.app.prefs.app['locale'] = \
                        locales[thisPref]
                    self.prefsCfg[sectionName][prefName] = \
                        locales[thisPref]
                    continue

                # remove invisible trailing whitespace:
                if hasattr(thisPref, 'strip'):
                    thisPref = thisPref.strip()
                # regularize the display format for keybindings
                if sectionName == 'keyBindings':
                    thisPref = thisPref.replace(' ', '')
                    thisPref = '+'.join([part.capitalize()
                                         for part in thisPref.split('+')])
                    if platform.system() == 'Darwin':
                        # key-bindings were displayed as 'Cmd+O', revert to
                        # 'Ctrl+O' internally
                        thisPref = re_cmd2ctrl.sub('Ctrl+', thisPref)
                self.prefsCfg[sectionName][prefName] = thisPref

                # make sure list values are converted back to lists (from str)
                if self.prefsSpec[sectionName][prefName].startswith('list'):
                    try:
                        # if thisPref is not a null string, do eval() to get a
                        # list.
                        if thisPref == '' or type(thisPref) == list:
                            newVal = thisPref
                        else:
                            newVal = eval(thisPref)
                    except Exception:
                        # if eval() failed, show warning dialog and return
                        try:
                            pLabel = _localized[prefName]
                            sLabel = _localized[sectionName]
                        except Exception:
                            pLabel = prefName
                            sLabel = sectionName
                        txt = _translate(
                            'Invalid value in "%(pref)s" ("%(section)s" Tab)')
                        msg = txt % {'pref': pLabel, 'section': sLabel}
                        title = _translate('Error')
                        warnDlg = dialogs.MessageDialog(parent=self,
                                                        message=msg,
                                                        type='Info',
                                                        title=title)
                        warnDlg.ShowModal()
                        return
                    if type(newVal) != list:
                        self.prefsCfg[sectionName][prefName] = [newVal]
                    else:
                        self.prefsCfg[sectionName][prefName] = newVal
                elif self.prefsSpec[sectionName][prefName].startswith('option'):
                    vals = self.prefsSpec[sectionName][prefName].replace(
                        "option(", "").replace("'", "")
                    # item -1 is 'default=x' from spec
                    options = vals.replace(", ", ",").split(',')[:-1]
                    self.prefsCfg[sectionName][prefName] = options[thisPref]

        self.app.prefs.saveUserPrefs()  # includes a validation
        # maybe then go back and set GUI from prefs again, because validation
        # may have changed vals?
        # > sure, why not? - mdc
        self.populatePrefs()

        # after validation, update the UI
        self.app.theme = self.app.theme
        self.updateCoderUI()
        self.updateBuilderUI()