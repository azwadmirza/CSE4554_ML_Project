def _generate_interp_custom(coord_func, ndim, large_int, yshape, mode, cval,
                            order, name='', integer_output=False):
    """
    Args:
        coord_func (function): generates code to do the coordinate
            transformation. See for example, `_get_coord_shift`.
        ndim (int): The number of dimensions.
        large_int (bool): If true use Py_ssize_t instead of int for indexing.
        yshape (tuple): Shape of the output array.
        mode (str): Signal extension mode to use at the array boundaries
        cval (float): constant value used when `mode == 'constant'`.
        name (str): base name for the interpolation kernel
        integer_output (bool): boolean indicating whether the output has an
            integer type.

    Returns:
        operation (str): code body for the ElementwiseKernel
        name (str): name for the ElementwiseKernel
    """

    ops = []
    ops.append('double out = 0.0;')

    if large_int:
        uint_t = 'size_t'
        int_t = 'ptrdiff_t'
    else:
        uint_t = 'unsigned int'
        int_t = 'int'

    # determine strides for x along each axis
    for j in range(ndim):
        ops.append(
            'const {int_t} xsize_{j} = x.shape()[{j}];'.format(
                int_t=int_t, j=j)
        )
    ops.append('const {uint_t} sx_{j} = 1;'.format(uint_t=uint_t, j=ndim - 1))
    for j in range(ndim - 1, 0, -1):
        ops.append(
            'const {uint_t} sx_{jm} = sx_{j} * xsize_{j};'.format(
                uint_t=uint_t, jm=j - 1, j=j,
            )
        )

    # create in_coords array to store the unraveled indices
    ops.append(_unravel_loop_index(yshape, uint_t))

    # compute the transformed (target) coordinates, c_j
    ops = ops + coord_func(ndim)

    if mode == 'constant':
        # use cval if coordinate is outside the bounds of x
        _cond = ' || '.join(
            ['(c_{j} < 0) || (c_{j} > xsize_{j} - 1)'.format(j=j)
             for j in range(ndim)])
        ops.append("""
        if ({cond})
        {{
            out = (double){cval};
        }}
        else
        {{""".format(cond=_cond, cval=cval))

    if order == 0:
        for j in range(ndim):
            # determine nearest neighbor
            ops.append("""
            {int_t} cf_{j} = ({int_t})lrint((double)c_{j});
            """.format(int_t=int_t, j=j))

            # handle boundary
            if mode != 'constant':
                ixvar = 'cf_{j}'.format(j=j)
                ops.append(
                    _util._generate_boundary_condition_ops(
                        mode, ixvar, 'xsize_{}'.format(j)))

            # sum over ic_j will give the raveled coordinate in the input
            ops.append("""
            {int_t} ic_{j} = cf_{j} * sx_{j};
            """.format(int_t=int_t, j=j))
        _coord_idx = ' + '.join(['ic_{}'.format(j) for j in range(ndim)])
        ops.append("""
            out = x[{coord_idx}];""".format(coord_idx=_coord_idx))

    elif order == 1:
        for j in range(ndim):
            # get coordinates for linear interpolation along axis j
            ops.append("""
            {int_t} cf_{j} = ({int_t})floor((double)c_{j});
            {int_t} cc_{j} = cf_{j} + 1;
            {int_t} n_{j} = (c_{j} == cf_{j}) ? 1 : 2;  // points needed
            """.format(int_t=int_t, j=j))

            # handle boundaries for extension modes.
            ops.append("""
            {int_t} cf_bounded_{j} = cf_{j};
            {int_t} cc_bounded_{j} = cc_{j};
            """.format(int_t=int_t, j=j))
            if mode != 'constant':
                ixvar = 'cf_bounded_{j}'.format(j=j)
                ops.append(
                    _util._generate_boundary_condition_ops(
                        mode, ixvar, 'xsize_{}'.format(j)))
                ixvar = 'cc_bounded_{j}'.format(j=j)
                ops.append(
                    _util._generate_boundary_condition_ops(
                        mode, ixvar, 'xsize_{}'.format(j)))

            ops.append("""
            for (int s_{j} = 0; s_{j} < n_{j}; s_{j}++)
                {{
                    W w_{j};
                    {int_t} ic_{j};
                    if (s_{j} == 0)
                    {{
                        w_{j} = (W)cc_{j} - c_{j};
                        ic_{j} = cf_bounded_{j} * sx_{j};
                    }} else
                    {{
                        w_{j} = c_{j} - (W)cf_{j};
                        ic_{j} = cc_bounded_{j} * sx_{j};
                    }}""".format(int_t=int_t, j=j))

        _weight = ' * '.join(['w_{j}'.format(j=j) for j in range(ndim)])
        _coord_idx = ' + '.join(['ic_{j}'.format(j=j) for j in range(ndim)])
        ops.append("""
        X val = x[{coord_idx}];
        out += val * ({weight});""".format(
            coord_idx=_coord_idx, weight=_weight))
        ops.append('}' * ndim)

    if mode == 'constant':
        ops.append('}')

    if integer_output:
        ops.append('y = (Y)rint((double)out);')
    else:
        ops.append('y = (Y)out;')
    operation = '\n'.join(ops)

    name = 'interpolate_{}_order{}_{}_{}d_y{}'.format(
        name, order, mode, ndim, "_".join(["{}".format(j) for j in yshape]),
    )
    if uint_t == 'size_t':
        name += '_i64'
    return operation, name