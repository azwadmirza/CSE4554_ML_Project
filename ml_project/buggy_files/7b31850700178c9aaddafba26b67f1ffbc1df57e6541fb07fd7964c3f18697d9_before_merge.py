    def __init__(self, rrule, conf, startdt):
        self._conf = conf
        self._startdt = startdt
        self._rrule = rrule
        self.repeat = bool(rrule)
        self._allow_edit = not self.repeat or self.check_understood_rrule(rrule)
        self.repeat_box = urwid.CheckBox(
            'Repeat: ', state=self.repeat, on_state_change=self.check_repeat,
        )

        if "UNTIL" in self._rrule:
            self._until = "Until"
        elif "COUNT" in self._rrule:
            self._until = "Repetitions"
        else:
            self._until = "Forever"

        recurrence = self._rrule['freq'][0].lower() if self._rrule else "weekly"
        self.recurrence_choice = Choice(
            ["daily", "weekly", "monthly", "yearly"],
            recurrence,
            callback=self.rebuild,
        )
        self.interval_edit = PositiveIntEdit(
            caption='every:',
            edit_text=str(self._rrule.get('INTERVAL', [1])[0]),
        )
        self.until_choice = Choice(
            ["Forever", "Until", "Repetitions"], self._until, callback=self.rebuild,
        )

        count = str(self._rrule.get('COUNT', [1])[0])
        self.repetitions_edit = PositiveIntEdit(edit_text=count)

        until = self._rrule.get('UNTIL', [None])[0]
        if until is None and isinstance(self._startdt, datetime):
            until = self._startdt.date()
        elif until is None:
            until = self._startdt

        if isinstance(until, datetime):
            until = datetime.date()
        self.until_edit = DateEdit(
            until, self._conf['locale']['longdateformat'],
            lambda _: None, self._conf['locale']['weeknumbers'],
            self._conf['locale']['firstweekday'],
        )

        self._rebuild_weekday_checks()
        self._rebuild_monthly_choice()
        self._pile = pile = NPile([urwid.Text('')])
        urwid.WidgetWrap.__init__(self, pile)
        self.rebuild()