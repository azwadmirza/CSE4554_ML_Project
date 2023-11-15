    def update_info(self, role=None, status=None):
        """Edit an existing collaboration on Box

        :param role:
            The new role for this collaboration or None to leave unchanged
        :type role:
            :class:`CollaborationRole`
        :param status:
            The new status for this collaboration or None to leave unchanged. A pending collaboration can be set to
            accepted or rejected if permissions allow it.
        :type status:
            :class:`CollaborationStatus`
        :returns:
            Whether or not the edit was successful.
        :rtype:
            `bool`
        :raises:
            :class:`BoxAPIException` if current user doesn't have permissions to edit the collaboration.
        """
        # pylint:disable=arguments-differ
        data = {}
        if role:
            data['role'] = role
        if status:
            data['status'] = status
        return super(Collaboration, self).update_info(data=data)