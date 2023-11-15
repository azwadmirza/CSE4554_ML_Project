    def issue_ticket(
        self, conversation_id: Text, lock_lifetime: Union[float, int] = LOCK_LIFETIME
    ) -> int:
        """Issue new ticket with `lock_lifetime` for lock associated with
        `conversation_id`.

        Creates a new lock if none is found.
        """

        lock = self.get_or_create_lock(conversation_id)
        ticket = lock.issue_ticket(lock_lifetime)

        while True:
            try:
                self.ensure_ticket_available(lock)
                break
            except TicketExistsError:
                # issue a new ticket if current ticket number has been issued twice
                logger.exception(
                    "Ticket could not be issued. Issuing new ticket and retrying..."
                )
                ticket = lock.issue_ticket(lock_lifetime)

        self.save_lock(lock)

        return ticket