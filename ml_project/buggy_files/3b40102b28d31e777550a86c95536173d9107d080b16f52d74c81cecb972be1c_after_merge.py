    def toggle_delete(self):
        # TODO unify, either directly delete *normal* events as well
        # or stage recurring deletion as well
        def delete_this(_):
            self.event.delete_instance(self.event.recurrence_id)
            self.eventcolumn.pane.collection.update(self.event)
            self.eventcolumn.pane.window.backtrack()

        def delete_future(_):
            self.eventcolumn.pane.window.backtrack()

        def delete_all(_):
            if self.uid in self.eventcolumn.pane.deleted:
                self.eventcolumn.pane.deleted.remove(self.uid)
            else:
                self.eventcolumn.pane.deleted.append(self.uid)
            self.eventcolumn.pane.window.backtrack()

        if self.event.readonly:
            self.eventcolumn.pane.window.alert(
                ('light red',
                 'Calendar {} is read-only.'.format(self.event.calendar)))
            return
        if self.uid in self.eventcolumn.pane.deleted:
            self.eventcolumn.pane.deleted.remove(self.uid)
        else:
            if self.event.recurring:
                overlay = urwid.Overlay(
                    DeleteDialog(
                        delete_this,
                        delete_future,
                        delete_all,
                        self.eventcolumn.pane.window.backtrack,
                    ),
                    self.eventcolumn.pane,
                    'center', ('relative', 70), ('relative', 70), None)
                self.eventcolumn.pane.window.open(overlay)
            else:
                self.eventcolumn.pane.deleted.append(self.uid)
        self.set_title()