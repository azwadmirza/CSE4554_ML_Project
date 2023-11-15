    def notifier(self, trait_dict, removed, added, changed):
        """ Fire the TraitDictEvent with the provided parameters.

        Parameters
        ----------
        trait_dict : dict
            The complete dictionary.
        removed : dict
            Dict of removed items.
        added : dict
            Dict of added items.
        changed : dict
            Dict of changed items.
        """

        if self.name_items is None:
            return

        object = self.object()

        if object is None:
            return

        if getattr(object, self.name) is not self:
            # Workaround having this dict inside another container which
            # also uses the name_items trait for notification.
            # See enthought/traits#25
            return

        event = TraitDictEvent(removed=removed, added=added, changed=changed)
        items_event = self.trait.items_event()
        object.trait_items_event(self.name_items, event, items_event)