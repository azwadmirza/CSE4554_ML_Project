    def _match_key(self, sequence):
        """Try to match a given keystring with any bound keychain.

        Args:
            sequence: The command string to find.

        Return:
            A tuple (matchtype, binding).
                matchtype: Match.definitive, Match.partial or Match.none.
                binding: - None with Match.partial/Match.none.
                         - The found binding with Match.definitive.
        """
        assert sequence
        assert not isinstance(sequence, str)
        result = QKeySequence.NoMatch

        for seq, cmd in self.bindings.items():
            assert not isinstance(seq, str), seq
            match = sequence.matches(seq)
            if match == QKeySequence.ExactMatch:
                return (match, cmd)
            elif match == QKeySequence.PartialMatch:
                result = QKeySequence.PartialMatch

        return (result, None)