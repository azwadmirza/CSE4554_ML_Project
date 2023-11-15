    def _check_sigs_and_hash(self, room_version: str, pdu: EventBase) -> Deferred:
        return make_deferred_yieldable(
            self._check_sigs_and_hashes(room_version, [pdu])[0]
        )