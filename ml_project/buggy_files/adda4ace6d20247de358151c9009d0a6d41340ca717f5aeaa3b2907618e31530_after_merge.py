    def reset(cls):
        """Reset credentials by removing file.

        This is used by `streamlit activate reset` in case a user wants
        to start over.
        """
        c = Credentials.get_current()
        c.activation = None

        try:
            os.remove(c._conf_file)
        except OSError as e:
            LOGGER.error("Error removing credentials file: %s" % e)