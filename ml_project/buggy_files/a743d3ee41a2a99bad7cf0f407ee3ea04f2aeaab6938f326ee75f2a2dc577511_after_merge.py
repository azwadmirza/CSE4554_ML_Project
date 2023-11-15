    def search_user_directory(self, term: str) -> List[User]:
        """
        Search user directory for a given term, returning a list of users
        Args:
            term: term to be searched for
        Returns:
            user_list: list of users returned by server-side search
        """
        try:
            response = self.api._send("POST", "/user_directory/search", {"search_term": term})
        except MatrixRequestError as ex:
            if ex.code >= 500:
                log.error(
                    "Ignoring Matrix error in `search_user_directory`",
                    exc_info=ex,
                    term=term,
                )
                return list()
            else:
                raise ex
        try:
            return [
                User(self.api, _user["user_id"], _user["display_name"])
                for _user in response["results"]
            ]
        except KeyError:
            return list()