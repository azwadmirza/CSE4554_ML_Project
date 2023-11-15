    def transform(
        self,
        xx: Any,
        yy: Any,
        zz: Any = None,
        tt: Any = None,
        radians: bool = False,
        errcheck: bool = False,
        direction: Union[TransformDirection, str] = TransformDirection.FORWARD,
    ) -> Any:
        """
        Transform points between two coordinate systems.

        .. versionadded:: 2.1.1 errcheck
        .. versionadded:: 2.2.0 direction

        Parameters
        ----------
        xx: scalar or array (numpy or python)
            Input x coordinate(s).
        yy: scalar or array (numpy or python)
            Input y coordinate(s).
        zz: scalar or array (numpy or python), optional
            Input z coordinate(s).
        tt: scalar or array (numpy or python), optional
            Input time coordinate(s).
        radians: boolean, optional
            If True, will expect input data to be in radians and will return radians
            if the projection is geographic. Default is False (degrees). Ignored for
            pipeline transformations.
        errcheck: boolean, optional (default False)
            If True an exception is raised if the transformation is invalid.
            By default errcheck=False and an invalid transformation
            returns ``inf`` and no exception is raised.
        direction: pyproj.enums.TransformDirection, optional
            The direction of the transform.
            Default is :attr:`pyproj.enums.TransformDirection.FORWARD`.


        Example:

        >>> from pyproj import Transformer
        >>> transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
        >>> x3, y3 = transformer.transform(33, 98)
        >>> "%.3f  %.3f" % (x3, y3)
        '10909310.098  3895303.963'
        >>> pipeline_str = (
        ...     "+proj=pipeline +step +proj=longlat +ellps=WGS84 "
        ...     "+step +proj=unitconvert +xy_in=rad +xy_out=deg"
        ... )
        >>> pipe_trans = Transformer.from_pipeline(pipeline_str)
        >>> xt, yt = pipe_trans.transform(2.1, 0.001)
        >>> "%.3f  %.3f" % (xt, yt)
        '2.100  0.001'
        >>> transproj = Transformer.from_crs(
        ...     {"proj":'geocent', "ellps":'WGS84', "datum":'WGS84'},
        ...     "EPSG:4326",
        ...     always_xy=True,
        ... )
        >>> xpj, ypj, zpj = transproj.transform(
        ...     -2704026.010,
        ...     -4253051.810,
        ...     3895878.820,
        ...     radians=True,
        ... )
        >>> "%.3f %.3f %.3f" % (xpj, ypj, zpj)
        '-2.137 0.661 -20.531'
        >>> transprojr = Transformer.from_crs(
        ...     "EPSG:4326",
        ...     {"proj":'geocent', "ellps":'WGS84', "datum":'WGS84'},
        ...     always_xy=True,
        ... )
        >>> xpjr, ypjr, zpjr = transprojr.transform(xpj, ypj, zpj, radians=True)
        >>> "%.3f %.3f %.3f" % (xpjr, ypjr, zpjr)
        '-2704026.010 -4253051.810 3895878.820'
        >>> transformer = Transformer.from_proj("epsg:4326", 4326, skip_equivalent=True)
        >>> xeq, yeq = transformer.transform(33, 98)
        >>> "%.0f  %.0f" % (xeq, yeq)
        '33  98'

        """
        # process inputs, making copies that support buffer API.
        inx, xisfloat, xislist, xistuple = _copytobuffer(xx)
        iny, yisfloat, yislist, yistuple = _copytobuffer(yy)
        if zz is not None:
            inz, zisfloat, zislist, zistuple = _copytobuffer(zz)
        else:
            inz = None
        if tt is not None:
            intime, tisfloat, tislist, tistuple = _copytobuffer(tt)
        else:
            intime = None
        # call pj_transform.  inx,iny,inz buffers modified in place.
        self._transformer._transform(
            inx,
            iny,
            inz=inz,
            intime=intime,
            direction=direction,
            radians=radians,
            errcheck=errcheck,
        )
        # if inputs were lists, tuples or floats, convert back.
        outx = _convertback(xisfloat, xislist, xistuple, inx)
        outy = _convertback(yisfloat, yislist, xistuple, iny)
        return_data = (outx, outy)
        if inz is not None:
            return_data += (  # type: ignore
                _convertback(zisfloat, zislist, zistuple, inz),
            )
        if intime is not None:
            return_data += (  # type: ignore
                _convertback(tisfloat, tislist, tistuple, intime),
            )
        return return_data