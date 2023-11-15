def HeatMap(data, x=None, y=None, values=None, stat='count', xscale="categorical",
            yscale="categorical", xgrid=False, ygrid=False, **kw):
    """ Create a HeatMap chart using :class:`HeatMapBuilder <bokeh.charts.builder.heatmap_builder.HeatMapBuilder>`
    to render the geometry from values.

    A HeatMap is a 3 Dimensional chart that crosses two dimensions, then aggregates
    values if there are multiple that correspond to the intersection of the horizontal
    and vertical dimensions. The value that falls at the intersection is then mapped to a
    color in a palette. All values that map to the positions on the chart are binned into
    the same amount of bins as there are colors in the pallete.

    Args:
        values (iterable): iterable 2d representing the data series
            values matrix.

    In addition the the parameters specific to this chart,
    :ref:`userguide_charts_generic_arguments` are also accepted as keyword parameters.

    Returns:
        a new :class:`Chart <bokeh.charts.Chart>`

    Examples:

    .. bokeh-plot::
        :source-position: above

        from collections import OrderedDict
        from bokeh.charts import HeatMap, output_file, show

        # (dict, OrderedDict, lists, arrays and DataFrames are valid inputs)
        xyvalues = OrderedDict()
        xyvalues['apples'] = [4,5,8]
        xyvalues['bananas'] = [1,2,4]
        xyvalues['pears'] = [6,5,4]

        hm = HeatMap(xyvalues, title='Fruits')

        output_file('heatmap.html')
        show(hm)

    """
    kw['x'] = x
    kw['y'] = y
    kw['values'] = values
    chart = create_and_build(
        HeatMapBuilder, data, xscale=xscale, yscale=yscale,
        xgrid=xgrid, ygrid=ygrid, **kw
    )
    chart.add_tools(HoverTool(tooltips=[(stat, "@values")]))
    return chart