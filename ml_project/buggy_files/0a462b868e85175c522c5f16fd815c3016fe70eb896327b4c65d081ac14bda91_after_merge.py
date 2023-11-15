    def warm_users(self, users: List[User]) -> None:
        for user in users:
            user_id = user.user_id
            cached_displayname = self.userid_to_displayname.get(user_id)

            if cached_displayname is None:
                # The cache is cold, query and warm it.
                if not user.displayname:
                    # Handles an edge case where the Matrix federation does not
                    # have the profile for a given userid. The server response
                    # is roughly:
                    #
                    #   {"errcode":"M_NOT_FOUND","error":"Profile was not found"} or
                    #   {"errcode":"M_UNKNOWN","error":"Failed to fetch profile"}
                    try:
                        user.get_display_name()
                    except MatrixRequestError as ex:
                        # We ignore the error here and set user presence: SERVER_ERROR at the
                        # calling site
                        log.error(
                            "Ignoring Matrix error in `get_display_name`",
                            exc_info=ex,
                            user_id=user.user_id,
                        )

                if user.displayname is not None:
                    self.userid_to_displayname[user.user_id] = user.displayname

            elif user.displayname is None:
                user.displayname = cached_displayname

            elif user.displayname != cached_displayname:
                log.debug(
                    "User displayname changed!",
                    cached=cached_displayname,
                    current=user.displayname,
                )
                self.userid_to_displayname[user.user_id] = user.displayname