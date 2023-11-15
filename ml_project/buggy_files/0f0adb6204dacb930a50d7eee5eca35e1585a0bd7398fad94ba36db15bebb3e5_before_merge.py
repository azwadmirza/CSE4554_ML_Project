    def __add_station(self, uri):
        irfs = add_station(uri)

        if not irfs:
            qltk.ErrorMessage(
                None, _("No stations found"),
                _("No Internet radio stations were found at %s.") %
                util.escape(uri)).run()
            return

        irfs = filter(lambda station: station not in self.__fav_stations, irfs)
        if not irfs:
            qltk.WarningMessage(
                None, _("Unable to add station"),
                _("All stations listed are already in your library.")).run()

        if irfs:
            self.__fav_stations.add(irfs)