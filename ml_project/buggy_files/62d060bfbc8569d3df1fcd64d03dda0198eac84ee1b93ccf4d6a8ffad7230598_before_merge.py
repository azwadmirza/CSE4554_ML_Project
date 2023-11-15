    def update_by_date(self, this_date=date.today()):
        if this_date is None:   # this_date might be None
            return

        date_text = urwid.Text(
            this_date.strftime(self.eventcolumn.pane.conf['locale']['longdateformat']))
        events = sorted(self.eventcolumn.pane.collection.get_events_on(this_date))

        event_list = [
            urwid.AttrMap(U_Event(event, this_date=this_date, eventcolumn=self.eventcolumn),
                          'calendar ' + event.calendar, 'reveal focus') for event in events]
        event_count = len(event_list)
        if not event_list:
            event_list = [urwid.Text('no scheduled events')]
        self.list_walker = urwid.SimpleFocusListWalker(event_list)
        self._w = urwid.Frame(urwid.ListBox(self.list_walker), header=date_text)
        return event_count