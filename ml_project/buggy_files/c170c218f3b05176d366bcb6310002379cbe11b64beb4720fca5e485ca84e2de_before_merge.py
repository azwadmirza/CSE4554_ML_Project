    def _event_match(self, condition: dict, user_id: str) -> bool:
        pattern = condition.get("pattern", None)

        if not pattern:
            pattern_type = condition.get("pattern_type", None)
            if pattern_type == "user_id":
                pattern = user_id
            elif pattern_type == "user_localpart":
                pattern = UserID.from_string(user_id).localpart

        if not pattern:
            logger.warning("event_match condition with no pattern")
            return False

        # XXX: optimisation: cache our pattern regexps
        if condition["key"] == "content.body":
            body = self._event.content.get("body", None)
            if not body:
                return False

            return _glob_matches(pattern, body, word_boundary=True)
        else:
            haystack = self._get_value(condition["key"])
            if haystack is None:
                return False

            return _glob_matches(pattern, haystack)