    def load_file(self, path: mitmproxy.types.Path) -> None:
        """
            Load flows into the view, without processing them with addons.
        """
        spath = os.path.expanduser(path)
        try:
            with open(spath, "rb") as f:
                for i in io.FlowReader(f).stream():
                    # Do this to get a new ID, so we can load the same file N times and
                    # get new flows each time. It would be more efficient to just have a
                    # .newid() method or something.
                    self.add([i.copy()])
        except IOError as e:
            ctx.log.error(e.strerror)
        except exceptions.FlowReadException as e:
            ctx.log.error(str(e))