    async def on_POST(self, request):
        await self.auth.get_user_by_req(request, allow_guest=True)

        server = parse_string(request, "server", default=None)
        content = parse_json_object_from_request(request)

        limit = int(content.get("limit", 100))  # type: Optional[int]
        since_token = content.get("since", None)
        search_filter = content.get("filter", None)

        include_all_networks = content.get("include_all_networks", False)
        third_party_instance_id = content.get("third_party_instance_id", None)

        if include_all_networks:
            network_tuple = None
            if third_party_instance_id is not None:
                raise SynapseError(
                    400, "Can't use include_all_networks with an explicit network"
                )
        elif third_party_instance_id is None:
            network_tuple = ThirdPartyInstanceID(None, None)
        else:
            network_tuple = ThirdPartyInstanceID.from_string(third_party_instance_id)

        if limit == 0:
            # zero is a special value which corresponds to no limit.
            limit = None

        handler = self.hs.get_room_list_handler()
        if server and server != self.hs.config.server_name:
            try:
                data = await handler.get_remote_public_room_list(
                    server,
                    limit=limit,
                    since_token=since_token,
                    search_filter=search_filter,
                    include_all_networks=include_all_networks,
                    third_party_instance_id=third_party_instance_id,
                )
            except HttpResponseException as e:
                raise e.to_synapse_error()
        else:
            data = await handler.get_local_public_room_list(
                limit=limit,
                since_token=since_token,
                search_filter=search_filter,
                network_tuple=network_tuple,
            )

        return 200, data