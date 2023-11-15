    def __init__(
        self,
        conversion: Any,
        name: str = "undefined",
        cartesian_cs: Any = None,
        geodetic_crs: Any = None,
    ) -> None:
        """
        Parameters
        ----------
        conversion: Any
            Anything accepted by :meth:`pyproj.crs.CoordinateSystem.from_user_input`
            or a conversion from :ref:`coordinate_operation`.
        name: str, optional
            The name of the Projected CRS. Default is undefined.
        cartesian_cs: Any, optional
            Input to create a Cartesian Coordinate System.
            Anything accepted by :meth:`pyproj.crs.CoordinateSystem.from_user_input`
            or :class:`pyproj.crs.coordinate_system.Cartesian2DCS`.
        geodetic_crs: Any, optional
            Input to create the Geodetic CRS, a :class:`GeographicCRS` or
            anything accepted by :meth:`pyproj.crs.CRS.from_user_input`.
        """
        proj_crs_json = {
            "$schema": "https://proj.org/schemas/v0.2/projjson.schema.json",
            "type": "ProjectedCRS",
            "name": name,
            "base_crs": CRS.from_user_input(
                geodetic_crs or GeographicCRS()
            ).to_json_dict(),
            "conversion": CoordinateOperation.from_user_input(
                conversion
            ).to_json_dict(),
            "coordinate_system": CoordinateSystem.from_user_input(
                cartesian_cs or Cartesian2DCS()
            ).to_json_dict(),
        }
        super().__init__(proj_crs_json)