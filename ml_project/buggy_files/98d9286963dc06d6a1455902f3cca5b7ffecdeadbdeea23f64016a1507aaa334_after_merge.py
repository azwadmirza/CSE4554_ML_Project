    def _query_http(self, dl_path, repo_info, decode_body=True):
        """
        Download files via http
        """
        query = None
        response = None

        try:
            if "username" in repo_info:
                try:
                    if "password" in repo_info:
                        query = http.query(
                            dl_path,
                            text=True,
                            username=repo_info["username"],
                            password=repo_info["password"],
                            decode_body=decode_body,
                        )
                    else:
                        raise SPMException(
                            "Auth defined, but password is not set for username: '{0}'".format(
                                repo_info["username"]
                            )
                        )
                except SPMException as exc:
                    self.ui.error(six.text_type(exc))
            else:
                query = http.query(dl_path, text=True, decode_body=decode_body)
        except SPMException as exc:
            self.ui.error(six.text_type(exc))

        try:
            if query:
                if "SPM-METADATA" in dl_path:
                    response = salt.utils.yaml.safe_load(query.get("text", "{}"))
                else:
                    response = query.get("text")
            else:
                raise SPMException("Response is empty, please check for Errors above.")
        except SPMException as exc:
            self.ui.error(six.text_type(exc))

        return response