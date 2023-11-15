    def _check_sigs_and_hash(self, room_version, pdu):
        return make_deferred_yieldable(
            self._check_sigs_and_hashes(room_version, [pdu])[0]
        )