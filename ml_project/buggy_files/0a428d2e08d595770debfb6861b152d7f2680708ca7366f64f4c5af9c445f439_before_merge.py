        def _raise_terms_error(msg=""):
            raise errors.AnsibleError(
                "subelements lookup expects a list of two or three items, "
                + msg)