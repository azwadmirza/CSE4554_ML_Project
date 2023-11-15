    def _find_required_permission(self, request, service):
        """Find out what is the permission object id and the required
        permission.

        .. note::
            This method saves an attribute ``self.current_record`` used
            in :class:`kinto.core.resource.UserResource`.
        """
        # By default, it's a URI a and permission associated to the method.
        permission_object_id = self.get_permission_object_id(request)
        method = request.method.lower()
        required_permission = self.method_permissions.get(method)

        # For create permission, the object id is the plural endpoint.
        collection_path = six.text_type(service.collection_path)
        collection_path = collection_path.format(**request.matchdict)

        # In the case of a "PUT", check if the targetted record already
        # exists, return "write" if it does, "create" otherwise.
        if request.method.lower() == "put":
            resource = service.resource(request=request, context=self)
            try:
                record = resource.model.get_record(resource.record_id)
                # Save a reference, to avoid refetching from storage in
                # resource.
                self.current_record = record
            except storage_exceptions.RecordNotFoundError:
                # The record does not exist, the permission to create on
                # the related collection is required.
                permission_object_id = collection_path
                required_permission = "create"
            else:
                # For safe creations, the user needs a create permission.
                # See Kinto/kinto#792
                if request.headers.get('If-None-Match') == '*':
                    permission_object_id = collection_path
                    required_permission = "create"
                else:
                    required_permission = "write"

        return (permission_object_id, required_permission)