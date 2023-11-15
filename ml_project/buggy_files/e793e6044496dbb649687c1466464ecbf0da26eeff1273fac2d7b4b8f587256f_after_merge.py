    def __init__(
        self,
        name: str = "undefined",
        datum: Any = "urn:ogc:def:datum:EPSG::6326",
        ellipsoidal_cs: Any = None,
    ) -> None:
        """
        Parameters
        ----------
        name: str, optional
            Name of the CRS. Default is undefined.
        datum: Any, optional
            Anything accepted by :meth:`pyproj.crs.Datum.from_user_input` or
            a :class:`pyproj.crs.datum.CustomDatum`.
        ellipsoidal_cs: Any, optional
            Input to create an Ellipsoidal Coordinate System.
            Anything accepted by :meth:`pyproj.crs.CoordinateSystem.from_user_input`
            or an Ellipsoidal Coordinate System created from :ref:`coordinate_system`.
        """
        geographic_crs_json = {
            "$schema": "https://proj.org/schemas/v0.2/projjson.schema.json",
            "type": "GeographicCRS",
            "name": name,
            "datum": Datum.from_user_input(datum).to_json_dict(),
            "coordinate_system": CoordinateSystem.from_user_input(
                ellipsoidal_cs or Ellipsoidal2DCS()
            ).to_json_dict(),
        }
        super().__init__(geographic_crs_json)