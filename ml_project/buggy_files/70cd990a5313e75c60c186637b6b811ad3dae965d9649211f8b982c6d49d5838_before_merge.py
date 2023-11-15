    def _invalidate_get_users_with_receipts_in_room(
        self, room_id, receipt_type, user_id
    ):
        if receipt_type != "m.read":
            return

        # Returns either an ObservableDeferred or the raw result
        res = self.get_users_with_read_receipts_in_room.cache.get(
            room_id, None, update_metrics=False
        )

        # first handle the Deferred case
        if isinstance(res, defer.Deferred):
            if res.called:
                res = res.result
            else:
                res = None

        if res and user_id in res:
            # We'd only be adding to the set, so no point invalidating if the
            # user is already there
            return

        self.get_users_with_read_receipts_in_room.invalidate((room_id,))