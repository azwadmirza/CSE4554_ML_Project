    def notifier(self, trait_set, removed, added):
        """ Converts and consolidates the parameters to a TraitSetEvent and
        then fires the event.

        Parameters
        ----------
        trait_set : set
            The complete set
        removed : set
            Set of values that were removed.
        added : set
            Set of values that were added.
        """

        if self.name_items is None:
            return

        object = self.object()
        if object is None:
            return

        if getattr(object, self.name) is not self:
            # Workaround having this set inside another container which
            # also uses the name_items trait for notification.
            # Similar to enthought/traits#25
            return

        event = TraitSetEvent(removed=removed, added=added)
        items_event = self.trait.items_event()
        object.trait_items_event(self.name_items, event, items_event)