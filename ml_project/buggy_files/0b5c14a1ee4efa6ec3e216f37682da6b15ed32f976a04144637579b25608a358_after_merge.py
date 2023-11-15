    def __init__(self, data_func, units_func):
        """
        Create an ifunc from a data function and units function.

        Args:

        * data_func:

            Function to be applied to one or two data arrays, which
            are given as positional arguments. Should return another
            data array, with the same shape as the first array.

            Can also have keyword arguments.

        * units_func:

            Function to calculate the unit of the resulting cube.
            Should take the cube(s) as input and return
            an instance of :class:`cf_units.Unit`.

        Returns:
            An ifunc.

        **Example usage 1** Using an existing numpy ufunc, such as numpy.sin
        for the data function and a simple lambda function for the units
        function::

            sine_ifunc = iris.analysis.maths.IFunc(
                numpy.sin, lambda cube: cf_units.Unit('1'))
            sine_cube = sine_ifunc(cube)

        **Example usage 2** Define a function for the data arrays of two cubes
        and define a units function that checks the units of the cubes
        for consistency, before giving the resulting cube the same units
        as the first cube::

            def ws_data_func(u_data, v_data):
                return numpy.sqrt( u_data**2 + v_data**2 )

            def ws_units_func(u_cube, v_cube):
                if u_cube.units != getattr(v_cube, 'units', u_cube.units):
                    raise ValueError("units do not match")
                return u_cube.units

            ws_ifunc = iris.analysis.maths.IFunc(ws_data_func, ws_units_func)
            ws_cube = ws_ifunc(u_cube, v_cube, new_name='wind speed')

        **Example usage 3** Using a data function that allows a keyword
        argument::

            cs_ifunc = iris.analysis.maths.IFunc(numpy.cumsum,
                lambda a: a.units)
            cs_cube = cs_ifunc(cube, axis=1)
        """

        if hasattr(data_func, 'nin'):
            self.nin = data_func.nin
        else:
            if six.PY2:
                (args, _, _, defaults) = inspect.getargspec(data_func)
                self.nin = len(args) - (
                    len(defaults) if defaults is not None else 0)
            else:
                sig = inspect.signature(data_func)
                args = [param for param in sig.parameters.values()
                        if (param.kind != param.KEYWORD_ONLY and
                            param.default is param.empty)]
                self.nin = len(args)

        if self.nin not in [1, 2]:
            msg = ('{} requires {} input data arrays, the IFunc class '
                   'currently only supports functions requiring 1 or two '
                   'data arrays as input.')
            raise ValueError(msg.format(data_func.__name__, self.nin))

        if hasattr(data_func, 'nout'):
            if data_func.nout != 1:
                msg = ('{} returns {} objects, the IFunc class currently '
                       'only supports functions returning a single object.')
                raise ValueError(msg.format(data_func.__name__,
                                            data_func.nout))

        self.data_func = data_func

        self.units_func = units_func