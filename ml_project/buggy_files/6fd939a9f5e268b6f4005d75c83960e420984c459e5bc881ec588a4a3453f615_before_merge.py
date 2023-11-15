    def write(cls, s, file=None, end="\n", nolock=False):
        """
        Print a message via tqdm (without overlap with bars)
        """
        fp = file if file is not None else sys.stdout
        with cls.external_write_mode(file=file, nolock=nolock):
            # Write the message
            fp.write(s)
            fp.write(end)