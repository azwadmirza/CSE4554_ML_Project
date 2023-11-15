    def __init__(self, master, base):
        self.master = master
        self.windows = dict(
            flowlist = flowlist.FlowListBox(master),
            flowview = flowview.FlowView(master),
            commands = commands.Commands(master),
            keybindings = keybindings.KeyBindings(master),
            options = options.Options(master),
            help = help.HelpView(master),
            eventlog = eventlog.EventLog(master),

            edit_focus_query = grideditor.QueryEditor(master),
            edit_focus_cookies = grideditor.CookieEditor(master),
            edit_focus_setcookies = grideditor.SetCookieEditor(master),
            edit_focus_form = grideditor.RequestFormEditor(master),
            edit_focus_path = grideditor.PathEditor(master),
            edit_focus_request_headers = grideditor.RequestHeaderEditor(master),
            edit_focus_response_headers = grideditor.ResponseHeaderEditor(master),
        )
        self.stack = [base]
        self.overlay = None