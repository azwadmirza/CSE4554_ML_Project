    def get_all_possible_names(self, season=-1):
        """Get every possible variation of the name for a particular show.

        Includes indexer name, and any scene exception names, and country code
        at the end of the name (e.g. "Show Name (AU)".

        show: a Series object that we should get the names of
        Returns: all possible show names
        """
        show_names = get_scene_exceptions(self, season)
        show_names.add(self.name)

        new_show_names = set()

        if not self.is_anime:
            country_list = {}
            # add the country list
            country_list.update(countryList)
            # add the reversed mapping of the country list
            country_list.update({v: k for k, v in viewitems(countryList)})

            for name in show_names:
                if not name:
                    continue

                # if we have "Show Name Australia" or "Show Name (Australia)"
                # this will add "Show Name (AU)" for any countries defined in
                # common.countryList (and vice versa)
                for country in country_list:
                    pattern_1 = ' {0}'.format(country)
                    pattern_2 = ' ({0})'.format(country)
                    replacement = ' ({0})'.format(country_list[country])
                    if name.endswith(pattern_1):
                        new_show_names.add(name.replace(pattern_1, replacement))
                    elif name.endswith(pattern_2):
                        new_show_names.add(name.replace(pattern_2, replacement))

        return show_names.union(new_show_names)