    def func(self):
        """
        Main puppet method
        """
        account = self.account
        session = self.session

        new_character = None
        character_candidates = []

        if not self.args:
            character_candidates = [account.db._last_puppet] or []
            if not character_candidates:
                self.msg("Usage: ic <character>")
                return
        else:
            # argument given

            if account.db._playable_characters:
                # look at the playable_characters list first
                character_candidates.extend(
                    account.search(
                        self.args,
                        candidates=account.db._playable_characters,
                        search_object=True,
                        quiet=True,
                    )
                )

            if account.locks.check_lockstring(account, "perm(Builder)"):
                # builders and higher should be able to puppet more than their
                # playable characters.
                if session.puppet:
                    # start by local search - this helps to avoid the user
                    # getting locked into their playable characters should one
                    # happen to be named the same as another. We replace the suggestion
                    # from playable_characters here - this allows builders to puppet objects
                    # with the same name as their playable chars should it be necessary
                    # (by going to the same location).
                    character_candidates = [
                        char
                        for char in session.puppet.search(self.args, quiet=True)
                        if char.access(account, "puppet")
                    ]
                if not character_candidates:
                    # fall back to global search only if Builder+ has no
                    # playable_characers in list and is not standing in a room
                    # with a matching char.
                    character_candidates.extend(
                        [
                            char
                            for char in search.object_search(self.args)
                            if char.access(account, "puppet")
                        ]
                    )

        # handle possible candidates
        if not character_candidates:
            self.msg("That is not a valid character choice.")
            return
        if len(character_candidates) > 1:
            self.msg(
                "Multiple targets with the same name:\n %s"
                % ", ".join("%s(#%s)" % (obj.key, obj.id) for obj in character_candidates)
            )
            return
        else:
            new_character = character_candidates[0]

        # do the puppet puppet
        try:
            account.puppet_object(session, new_character)
            account.db._last_puppet = new_character
            logger.log_sec(
                "Puppet Success: (Caller: %s, Target: %s, IP: %s)."
                % (account, new_character, self.session.address)
            )
        except RuntimeError as exc:
            self.msg("|rYou cannot become |C%s|n: %s" % (new_character.name, exc))
            logger.log_sec(
                "Puppet Failed: %s (Caller: %s, Target: %s, IP: %s)."
                % (exc, account, new_character, self.session.address)
            )