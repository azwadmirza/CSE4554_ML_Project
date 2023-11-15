    def convert(self, names, type_="entities", filter_matches=False):
        """Return a list of converted Alexa devices based on names.

        Names may be matched either by serialNumber, accountName, or
        Homeassistant entity_id and can return any of the above plus entities

        Parameters
        ----------
        names : list(string)
            A list of names to convert
        type_ : string
            The type to return entities, entity_ids, serialnumbers, names
        filter_matches : bool
            Whether non-matching items are removed from the returned list.

        Returns
        -------
        list(string)
            List of home assistant entity_ids

        """
        devices = []
        if isinstance(names, str):
            names = [names]
        for item in names:
            matched = False
            for alexa in self.devices:
                _LOGGER.debug(
                    "Testing item: %s against (%s, %s, %s, %s)",
                    item,
                    alexa,
                    alexa.name,
                    hide_serial(alexa.unique_id),
                    alexa.entity_id,
                )
                if item in (alexa, alexa.name, alexa.unique_id, alexa.entity_id):
                    if type_ == "entities":
                        converted = alexa
                    elif type_ == "serialnumbers":
                        converted = alexa.unique_id
                    elif type_ == "names":
                        converted = alexa.name
                    elif type_ == "entity_ids":
                        converted = alexa.entity_id
                    devices.append(converted)
                    matched = True
                    _LOGGER.debug("Converting: %s to (%s): %s", item, type_, converted)
            if not filter_matches and not matched:
                devices.append(item)
        return devices