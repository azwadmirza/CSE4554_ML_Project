    def __init__(self, request):
        # Make it available for the authorization policy.
        self.prefixed_userid = getattr(request, "prefixed_userid", None)

        self._check_permission = request.registry.permission.check_permission

        # Partial collections of ProtectedResource:
        self.shared_ids = []

        # Store service, resource, record and required permission.
        service = utils.current_service(request)

        is_on_resource = (service is not None and
                          hasattr(service, 'viewset') and
                          hasattr(service, 'resource'))

        if is_on_resource:
            self.on_collection = getattr(service, "type", None) == "collection"
            self.permission_object_id = self.get_permission_object_id(request)

            # Decide what the required unbound permission is depending on the
            # method that's being requested.
            if request.method.lower() == "put":
                # In the case of a "PUT", check if the targetted record already
                # exists, return "write" if it does, "create" otherwise.

                # If the view exists, call it with the request and catch an
                # eventual NotFound.
                resource = service.resource(request=request, context=self)
                try:
                    resource.collection.get_record(resource.record_id)
                except storage_exceptions.RecordNotFoundError:
                    self.permission_object_id = service.collection_path.format(
                        **request.matchdict)
                    self.required_permission = "create"
                else:
                    self.required_permission = "write"
            else:
                method = request.method.lower()
                self.required_permission = self.method_permissions.get(method)

            self.resource_name = service.viewset.get_name(service.resource)

            if self.on_collection:
                object_id_match = self.get_permission_object_id(request, '*')
                self.get_shared_ids = functools.partial(
                    request.registry.permission.principals_accessible_objects,
                    object_id_match=object_id_match)

            settings = request.registry.settings
            setting = 'cliquet.%s_%s_principals' % (self.resource_name,
                                                    self.required_permission)
            self.allowed_principals = aslist(settings.get(setting, ''))