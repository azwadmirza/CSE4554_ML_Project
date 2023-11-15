    async def on_GET(self, request, room_id, event_id):
        requester = await self.auth.get_user_by_req(request, allow_guest=False)
        await assert_user_is_admin(self.auth, requester.user)

        limit = parse_integer(request, "limit", default=10)

        # picking the API shape for symmetry with /messages
        filter_str = parse_string(request, b"filter", encoding="utf-8")
        if filter_str:
            filter_json = urlparse.unquote(filter_str)
            event_filter = Filter(
                json_decoder.decode(filter_json)
            )  # type: Optional[Filter]
        else:
            event_filter = None

        results = await self.room_context_handler.get_event_context(
            requester,
            room_id,
            event_id,
            limit,
            event_filter,
            use_admin_priviledge=True,
        )

        if not results:
            raise SynapseError(404, "Event not found.", errcode=Codes.NOT_FOUND)

        time_now = self.clock.time_msec()
        results["events_before"] = await self._event_serializer.serialize_events(
            results["events_before"], time_now
        )
        results["event"] = await self._event_serializer.serialize_event(
            results["event"], time_now
        )
        results["events_after"] = await self._event_serializer.serialize_events(
            results["events_after"], time_now
        )
        results["state"] = await self._event_serializer.serialize_events(
            results["state"], time_now
        )

        return 200, results