    def __init__(
        self,
        name: str,
        datum: Any,
        vertical_cs: Any = VerticalCS(),
        geoid_model: str = None,
    ) -> None:
        """
        Parameters
        ----------
        name: str
            The name of the Vertical CRS (e.g. NAVD88 height).
        datum: Any
            Anything accepted by :meth:`pyproj.crs.Datum.from_user_input`
        vertical_cs: Any, optional
            Input to create a Vertical Coordinate System accepted by
            :meth:`pyproj.crs.CoordinateSystem.from_user_input`
            or :class:`pyproj.crs.coordinate_system.VerticalCS`
        geoid_model: str, optional
            The name of the GEOID Model (e.g. GEOID12B).
        """
        vert_crs_json = {
            "$schema": "https://proj.org/schemas/v0.2/projjson.schema.json",
            "type": "VerticalCRS",
            "name": name,
            "datum": Datum.from_user_input(datum).to_json_dict(),
            "coordinate_system": CoordinateSystem.from_user_input(
                vertical_cs
            ).to_json_dict(),
        }
        if geoid_model is not None:
            vert_crs_json["geoid_model"] = {"name": geoid_model}

        super().__init__(vert_crs_json)