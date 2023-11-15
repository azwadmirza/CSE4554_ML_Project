    def __init__(self, eventcolumn):
        self.eventcolumn = eventcolumn
        self.events = None
        self.list_walker = None
        pile = urwid.Filler(urwid.Pile([]))
        urwid.WidgetWrap.__init__(self, pile)
        self.update_by_date()