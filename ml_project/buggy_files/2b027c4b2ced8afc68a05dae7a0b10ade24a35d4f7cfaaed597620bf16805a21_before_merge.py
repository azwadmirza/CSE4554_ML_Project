    def export_shipyard(self, data: Dict[str, Any], is_beta: bool) -> None:
        """
        export_shipyard updates EDDN with the current (lastStarport) station's outfitting options, if any.
        once the send is complete, this.shipyard is updated to the new data.

        :param data: dict containing the shipyard data
        :param is_beta: whether or not we are in beta mode
        """
        ships: Dict[str, Any] = data['lastStarport'].get('ships', {'shipyard_list': {}, 'unavailable_list': []})
        horizons: bool = is_horizons(
            data['lastStarport'].get('economies', {}),
            data['lastStarport'].get('modules', {}),
            ships
            )

        shipyard: List[Mapping[str, Any]] = sorted(
            itertools.chain(
                (ship['name'].lower() for ship in (ships['shipyard_list'] or {}).values()),
                ships['unavailable_list']
            )
        )
        # Don't send empty ships list - shipyard data is only guaranteed present if user has visited the shipyard.
        if shipyard and this.shipyard != (horizons, shipyard):
            self.send(data['commander']['name'], {
                '$schemaRef': f'https://eddn.edcd.io/schemas/shipyard/2{"/test" if is_beta else ""}',
                'message': OrderedDict([
                    ('timestamp',   data['timestamp']),
                    ('systemName',  data['lastSystem']['name']),
                    ('stationName', data['lastStarport']['name']),
                    ('marketId',    data['lastStarport']['id']),
                    ('horizons',    horizons),
                    ('ships',       shipyard),
                ]),
            })

        this.shipyard = (horizons, shipyard)