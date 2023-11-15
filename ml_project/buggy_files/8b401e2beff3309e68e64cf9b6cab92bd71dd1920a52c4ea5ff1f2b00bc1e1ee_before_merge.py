    async def on_GET(self, request):
        server = parse_string(request, "server", default=None)

        try:
            await self.auth.get_user_by_req(request, allow_guest=True)
        except InvalidClientCredentialsError as e:
            # Option to allow servers to require auth when accessing
            # /publicRooms via CS API. This is especially helpful in private
            # federations.
            if not self.hs.config.allow_public_rooms_without_auth:
                raise

            # We allow people to not be authed if they're just looking at our
            # room list, but require auth when we proxy the request.
            # In both cases we call the auth function, as that has the side
            # effect of logging who issued this request if an access token was
            # provided.
            if server:
                raise e
            else:
                pass

        limit = parse_integer(request, "limit", 0)
        since_token = parse_string(request, "since", None)

        if limit == 0:
            # zero is a special value which corresponds to no limit.
            limit = None

        handler = self.hs.get_room_list_handler()
        if server:
            data = await handler.get_remote_public_room_list(
                server, limit=limit, since_token=since_token
            )
        else:
            data = await handler.get_local_public_room_list(
                limit=limit, since_token=since_token
            )

        return 200, data