        def delete_this(_):
            if self.event.ref == u'PROTO':
                instance = self.event.start
            else:
                instance = self.event.ref
            self.event.delete_instance(instance)

            self.eventcolumn.pane.collection.update(self.event)
            self.eventcolumn.pane.window.backtrack()