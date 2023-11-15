    def __init__(
        self,
        base_crs: Any,
        conversion: Any,
        ellipsoidal_cs: Any = Ellipsoidal2DCS(),
        name: str = "undefined",
    ) -> None:
        """
        Parameters
        ----------
        base_crs: Any
            Input to create the Geodetic CRS, a :class:`GeographicCRS` or
            anything accepted by :meth:`pyproj.crs.CRS.from_user_input`.
        conversion: Any
            Anything accepted by :meth:`pyproj.crs.CoordinateSystem.from_user_input`
            or a conversion from :ref:`coordinate_operation`.
        ellipsoidal_cs: Any, optional
            Input to create an Ellipsoidal Coordinate System.
            Anything accepted by :meth:`pyproj.crs.CoordinateSystem.from_user_input`
            or an Ellipsoidal Coordinate System created from :ref:`coordinate_system`.
        name: str, optional
            Name of the CRS. Default is undefined.
        """
        derived_geographic_crs_json = {
            "$schema": "https://proj.org/schemas/v0.2/projjson.schema.json",
            "type": "DerivedGeographicCRS",
            "name": name,
            "base_crs": CRS.from_user_input(base_crs).to_json_dict(),
            "conversion": CoordinateOperation.from_user_input(
                conversion
            ).to_json_dict(),
            "coordinate_system": CoordinateSystem.from_user_input(
                ellipsoidal_cs
            ).to_json_dict(),
        }
        super().__init__(derived_geographic_crs_json)