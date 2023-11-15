    def __init__(self, message, no_version_found=False):
        extra = (
            "{0}: Your dependencies could not be resolved. You likely have a "
            "mismatch in your sub-dependencies.\n  "
            "First try clearing your dependency cache with {1}, then try the original command again.\n "
            "Alternatively, you can use {2} to bypass this mechanism, then run "
            "{3} to inspect the situation.\n  "
            "Hint: try {4} if it is a pre-release dependency."
            "".format(
                crayons.red("Warning", bold=True),
                crayons.red("$ pipenv lock --clear"),
                crayons.red("$ pipenv install --skip-lock"),
                crayons.red("$ pipenv graph"),
                crayons.red("$ pipenv lock --pre"),
            ),
        )
        if "no version found at all" in message:
            no_version_found = True
        message = "{0} {1}".format(
            crayons.red("ERROR:", bold=True), crayons.yellow(message)
        )
        if no_version_found:
            message = "{0}\n{1}".format(
                message,
                crayons.blue(
                    "Please check your version specifier and version number. "
                    "See PEP440 for more information."
                )
            )
        super(ResolutionFailure, self).__init__(decode_for_output(message), extra=extra)