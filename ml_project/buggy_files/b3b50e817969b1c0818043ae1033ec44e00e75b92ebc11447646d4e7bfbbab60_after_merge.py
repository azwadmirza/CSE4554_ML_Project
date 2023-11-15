    def last_issued(self) -> int:
        """Return number of the ticket that was last added.

        Returns:
             Number of `Ticket` that was last added. `NO_TICKET_ISSUED` if no
             tickets exist.
        """

        ticket_number = self._ticket_number_for(-1)

        return ticket_number if ticket_number is not None else NO_TICKET_ISSUED