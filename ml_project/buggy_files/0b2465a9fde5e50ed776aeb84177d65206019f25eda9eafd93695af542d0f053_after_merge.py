    def export_outfitting(self, data: Mapping[str, Any], is_beta: bool) -> None:
        """
        export_outfitting updates EDDN with the current (lastStarport) station's outfitting options, if any.
        Once the send is complete, this.outfitting is updated with the given data.

        :param data: dict containing the outfitting data
        :param is_beta: whether or not we're currently in beta mode
        """
        modules: Dict[str, Any] = data['lastStarport'].get('modules')
        if not modules:
            logger.debug('modules was None')
            modules = {}

        ships: Dict[str, Any] = data['lastStarport'].get('ships')
        if not ships:
            logger.debug('ships was None')
            ships = {'shipyard_list': {}, 'unavailable_list': []}

        # Horizons flag - will hit at least Int_PlanetApproachSuite other than at engineer bases ("Colony"),
        # prison or rescue Megaships, or under Pirate Attack etc
        horizons: bool = is_horizons(
            data['lastStarport'].get('economies', {}),
            modules,
            ships
            )

        to_search: Iterator[Mapping[str, Any]] = filter(
            lambda m: self.MODULE_RE.search(m['name']) and m.get('sku') in (None, HORIZ_SKU) and
            m['name'] != 'Int_PlanetApproachSuite',
            modules.values()
        )

        outfitting: List[str] = sorted(
            self.MODULE_RE.sub(lambda match: match.group(0).capitalize(), mod['name'].lower()) for mod in to_search
        )
        # Don't send empty modules list - schema won't allow it
        if outfitting and this.outfitting != (horizons, outfitting):
            self.send(data['commander']['name'], {
                '$schemaRef': f'https://eddn.edcd.io/schemas/outfitting/2{"/test" if is_beta else ""}',
                'message': OrderedDict([
                    ('timestamp',   data['timestamp']),
                    ('systemName',  data['lastSystem']['name']),
                    ('stationName', data['lastStarport']['name']),
                    ('marketId',    data['lastStarport']['id']),
                    ('horizons',    horizons),
                    ('modules',     outfitting),
                ]),
            })

        this.outfitting = (horizons, outfitting)