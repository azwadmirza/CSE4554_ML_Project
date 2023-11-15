    def __init__(self):
        self.sheets = []  # list of BaseSheet; all sheets on the sheet stack
        self.allSheets = weakref.WeakKeyDictionary()  # [BaseSheet] -> sheetname (all non-precious sheets ever pushed)
        self.statuses = collections.OrderedDict()  # (priority, statusmsg) -> num_repeats; shown until next action
        self.statusHistory = []  # list of [priority, statusmsg, repeats] for all status messages ever
        self.lastErrors = []
        self.keystrokes = ''
        self.prefixWaiting = False
        self.scr = mock.MagicMock(__bool__=mock.Mock(return_value=False))  # disable curses in batch mode
        self.mousereg = []
        self.cmdlog = None  # CommandLog