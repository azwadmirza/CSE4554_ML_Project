    def _invalidate_get_users_with_receipts_in_room(self, room_id, receipt_type,
                                                    user_id):
        if receipt_type != "m.read":
            return

        # Returns an ObservableDeferred
        res = self.get_users_with_read_receipts_in_room.cache.get(
            room_id, None, update_metrics=False,
        )

        if res:
            if isinstance(res, defer.Deferred) and res.called:
                res = res.result
            if user_id in res:
                # We'd only be adding to the set, so no point invalidating if the
                # user is already there
                return

        self.get_users_with_read_receipts_in_room.invalidate((room_id,))