def setp(obj, *args, **kwargs):
    """
    Set a property on an artist object.

    matplotlib supports the use of :func:`setp` ("set property") and
    :func:`getp` to set and get object properties, as well as to do
    introspection on the object.  For example, to set the linestyle of a
    line to be dashed, you can do::

      >>> line, = plot([1,2,3])
      >>> setp(line, linestyle='--')

    If you want to know the valid types of arguments, you can provide
    the name of the property you want to set without a value::

      >>> setp(line, 'linestyle')
          linestyle: [ '-' | '--' | '-.' | ':' | 'steps' | 'None' ]

    If you want to see all the properties that can be set, and their
    possible values, you can do::

      >>> setp(line)
          ... long output listing omitted

    :func:`setp` operates on a single instance or a iterable of
    instances. If you are in query mode introspecting the possible
    values, only the first instance in the sequence is used. When
    actually setting values, all the instances will be set.  e.g.,
    suppose you have a list of two lines, the following will make both
    lines thicker and red::

      >>> x = arange(0,1.0,0.01)
      >>> y1 = sin(2*pi*x)
      >>> y2 = sin(4*pi*x)
      >>> lines = plot(x, y1, x, y2)
      >>> setp(lines, linewidth=2, color='r')

    :func:`setp` works with the MATLAB style string/value pairs or
    with python kwargs.  For example, the following are equivalent::

      >>> setp(lines, 'linewidth', 2, 'color', 'r')  # MATLAB style
      >>> setp(lines, linewidth=2, color='r')        # python style
    """

    if not cbook.iterable(obj):
        objs = [obj]
    else:
        objs = list(cbook.flatten(obj))

    insp = ArtistInspector(objs[0])

    if len(kwargs) == 0 and len(args) == 0:
        print('\n'.join(insp.pprint_setters()))
        return

    if len(kwargs) == 0 and len(args) == 1:
        print(insp.pprint_setters(prop=args[0]))
        return

    if len(args) % 2:
        raise ValueError('The set args must be string, value pairs')

    # put args into ordereddict to maintain order
    funcvals = OrderedDict()
    for i in range(0, len(args) - 1, 2):
        funcvals[args[i]] = args[i + 1]

    ret = [o.update(funcvals) for o in objs]
    ret.extend([o.set(**kwargs) for o in objs])
    return [x for x in cbook.flatten(ret)]