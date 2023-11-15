        def get_duplicate_exception_message(
            duplicates: List[Tuple[List[Text], Text]]
        ) -> Text:
            """Return a message given a list of duplicates."""

            message = ""
            for d, name in duplicates:
                if d:
                    if message:
                        message += "\n"
                    message += (
                        "Duplicate {0} in domain. "
                        "These {0} occur more than once in "
                        "the domain: '{1}'".format(name, "', '".join(d))
                    )
            return message