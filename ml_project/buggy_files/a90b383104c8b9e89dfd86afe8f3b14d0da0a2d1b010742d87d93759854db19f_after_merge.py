    def __init__(self, script, initScript = None, base = None,
            targetName = None, icon = None, shortcutName = None, 
            shortcutDir = None, copyright = None, trademarks = None):
        self.script = script
        self.initScript = initScript or "Console"
        self.base = base or "Console"
        self.targetName = targetName
        self.icon = icon
        self.shortcutName = shortcutName
        self.shortcutDir = shortcutDir
        self.copyright = copyright
        self.trademarks = trademarks