    def last_issued(self) -> int:
        """Return number of the ticket that was last added.

        Returns:
             Number of `Ticket` that was last added. `NO_TICKET_ISSUED` if no
             tickets exist.
        """

        ticket_number = self._ticket_number_for(-1)
        if ticket_number is not None:
            return ticket_number

        return NO_TICKET_ISSUED