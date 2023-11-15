    def get_puppet(self, session):
        """
        Get an object puppeted by this session through this account. This is
        the main method for retrieving the puppeted object from the
        account's end.

        Args:
            session (Session): Find puppeted object based on this session

        Returns:
            puppet (Object): The matching puppeted object, if any.

        """
        return session.puppet