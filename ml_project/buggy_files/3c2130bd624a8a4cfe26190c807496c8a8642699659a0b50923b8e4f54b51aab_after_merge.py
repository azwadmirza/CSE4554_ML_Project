    def from_sbdb(cls, name, **kwargs):
        """Return osculating `Orbit` by using `SBDB` from Astroquery.

        Parameters
        ----------
        name: string
            Name of the body to make the request.

        Returns
        -------
        ss: poliastro.twobody.orbit.Orbit
            Orbit corresponding to body_name

        Examples
        --------
        >>> from poliastro.twobody.orbit import Orbit
        >>> apophis_orbit = Orbit.from_sbdb('apophis')  # doctest: +REMOTE_DATA

        """
        from poliastro.bodies import Sun

        obj = SBDB.query(name, full_precision=True, **kwargs)

        if "count" in obj:
            # no error till now ---> more than one object has been found
            # contains all the name of the objects
            objects_name = obj["list"]["name"]
            objects_name_in_str = (
                ""  # used to store them in string form each in new line
            )
            for i in objects_name:
                objects_name_in_str += i + "\n"

            raise ValueError(
                str(obj["count"]) + " different objects found: \n" + objects_name_in_str
            )

        if "object" not in obj.keys():
            raise ValueError("Object {} not found".format(name))

        a = obj["orbit"]["elements"]["a"].to(u.AU) * u.AU
        ecc = float(obj["orbit"]["elements"]["e"]) * u.one
        inc = obj["orbit"]["elements"]["i"].to(u.deg) * u.deg
        raan = obj["orbit"]["elements"]["om"].to(u.deg) * u.deg
        argp = obj["orbit"]["elements"]["w"].to(u.deg) * u.deg

        # Since JPL provides Mean Anomaly (M) we need to make
        # the conversion to the true anomaly (\nu)
        nu = M_to_nu(obj["orbit"]["elements"]["ma"].to(u.deg) * u.deg, ecc)

        epoch = time.Time(obj["orbit"]["epoch"].to(u.d), format="jd")

        ss = cls.from_classical(
            Sun,
            a,
            ecc,
            inc,
            raan,
            argp,
            nu,
            epoch=epoch.tdb,
            plane=Planes.EARTH_ECLIPTIC,
        )

        return ss