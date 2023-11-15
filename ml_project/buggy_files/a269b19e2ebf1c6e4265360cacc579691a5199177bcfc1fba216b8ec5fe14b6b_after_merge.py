    def update_info(self, data, params=None, headers=None, **kwargs):
        """Update information about this object.

        Send a PUT to the object's base endpoint to modify the provided
        attributes.

        :param data:
            The updated information about this object.
            Must be JSON serializable.
            Update the object attributes in data.keys(). The semantics of the
            values depends on the the type and attributes of the object being
            updated. For details on particular semantics, refer to the Box
            developer API documentation <https://developer.box.com/>.
        :type data:
            `dict`
        :param params:
            (optional) Query string parameters for the request.
        :type params:
            `dict` or None
        :param headers:
            (optional) Extra HTTP headers for the request.
        :type headers:
            `dict` or None
        :param kwargs:
            Optional arguments that ``put`` takes.
        :return:
            The updated object.
            Return a new object of the same type, without modifying the
            original object passed as self.
            Construct the new object with all the default attributes that are
            returned from the endpoint.
        :rtype:
            :class:`BaseObject`
        """
        # pylint:disable=no-else-return
        url = self.get_url()
        box_response = self._session.put(url, data=json.dumps(data), params=params, headers=headers, **kwargs)
        if 'expect_json_response' in kwargs and not kwargs['expect_json_response']:
            return box_response.ok
        else:
            return self.translator.translate(
                session=self._session,
                response_object=box_response.json(),
            )