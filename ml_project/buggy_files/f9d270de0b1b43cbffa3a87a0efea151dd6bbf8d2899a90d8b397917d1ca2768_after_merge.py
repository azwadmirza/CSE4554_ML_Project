        def delete_this(_):
            self.event.delete_instance(self.event.recurrence_id)
            self.eventcolumn.pane.collection.update(self.event)
            self.eventcolumn.pane.window.backtrack()