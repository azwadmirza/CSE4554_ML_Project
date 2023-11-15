    def __add_station(self, uri):
        irfs = add_station(uri)
        if irfs is None:
            # Error, rather than empty list
            return
        if not irfs:
            ErrorMessage(
                None, _("No stations found"),
                _("No Internet radio stations were found at %s.") %
                util.escape(uri)).run()
            return

        irfs = set(irfs) - set(self.__fav_stations)
        if not irfs:
            WarningMessage(
                None, _("Unable to add station"),
                _("All stations listed are already in your library.")).run()

        if irfs:
            self.__fav_stations.add(irfs)