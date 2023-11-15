    def showAbout(self, event):
        logging.debug('PsychoPyApp: Showing about dlg')

        with io.open(os.path.join(self.prefs.paths['psychopy'],'LICENSE.txt'),
                     'r', encoding='utf-8-sig') as f:
            license = f.read()

        msg = _translate(
            "For stimulus generation and experimental control in python.\n"
            "PsychoPy depends on your feedback. If something doesn't work\n"
            "then let us know at psychopy-users@googlegroups.com")
        if parse_version(wx.__version__) >= parse_version('4.0a1'):
            info = wx.adv.AboutDialogInfo()
            showAbout = wx.adv.AboutBox
        else:
            info = wx.AboutDialogInfo()
            showAbout = wx.AboutBox
        if wx.version() >= '3.':
            icon = os.path.join(self.prefs.paths['resources'], 'psychopy.png')
            info.SetIcon(wx.Icon(icon, wx.BITMAP_TYPE_PNG, 128, 128))
        info.SetName('PsychoPy')
        info.SetVersion('v' + psychopy.__version__)
        info.SetDescription(msg)

        info.SetCopyright('(C) 2002-2018 Jonathan Peirce')
        info.SetWebSite('http://www.psychopy.org')
        info.SetLicence(license)
        info.AddDeveloper('Jonathan Peirce')
        info.AddDeveloper('Jeremy Gray')
        info.AddDeveloper('Sol Simpson')
        info.AddDeveloper(u'Jonas Lindel\xF8v')
        info.AddDeveloper('Yaroslav Halchenko')
        info.AddDeveloper('Erik Kastman')
        info.AddDeveloper('Michael MacAskill')
        info.AddDeveloper('Hiroyuki Sogo')
        info.AddDeveloper('David Bridges')
        info.AddDocWriter('Jonathan Peirce')
        info.AddDocWriter('Jeremy Gray')
        info.AddDocWriter('Rebecca Sharman')
        info.AddTranslator('Hiroyuki Sogo')

        if not self.testMode:
            showAbout(info)