    def post(self, api_key_api, requester_user):
        """
        Create a new entry.
        """

        permission_type = PermissionType.API_KEY_CREATE
        rbac_utils.assert_user_has_resource_api_permission(user_db=requester_user,
                                                           resource_api=api_key_api,
                                                           permission_type=permission_type)

        api_key_db = None
        api_key = None
        try:
            if not getattr(api_key_api, 'user', None):
                if requester_user:
                    api_key_api.user = requester_user.name
                else:
                    api_key_api.user = cfg.CONF.system_user.user

            try:
                User.get_by_name(api_key_api.user)
            except StackStormDBObjectNotFoundError:
                user_db = UserDB(name=api_key_api.user)
                User.add_or_update(user_db)

                extra = {'username': api_key_api.user, 'user': user_db}
                LOG.audit('Registered new user "%s".' % (api_key_api.user), extra=extra)

            # If key_hash is provided use that and do not create a new key. The assumption
            # is user already has the original api-key
            if not getattr(api_key_api, 'key_hash', None):
                api_key, api_key_hash = auth_util.generate_api_key_and_hash()
                # store key_hash in DB
                api_key_api.key_hash = api_key_hash
            api_key_db = ApiKey.add_or_update(ApiKeyAPI.to_model(api_key_api))
        except (ValidationError, ValueError) as e:
            LOG.exception('Validation failed for api_key data=%s.', api_key_api)
            abort(http_client.BAD_REQUEST, str(e))

        extra = {'api_key_db': api_key_db}
        LOG.audit('ApiKey created. ApiKey.id=%s' % (api_key_db.id), extra=extra)

        api_key_create_response_api = ApiKeyCreateResponseAPI.from_model(api_key_db)
        # Return real api_key back to user. A one-way hash of the api_key is stored in the DB
        # only the real value only returned at create time. Also, no masking of key here since
        # the user needs to see this value atleast once.
        api_key_create_response_api.key = api_key

        return Response(json=api_key_create_response_api, status=http_client.CREATED)