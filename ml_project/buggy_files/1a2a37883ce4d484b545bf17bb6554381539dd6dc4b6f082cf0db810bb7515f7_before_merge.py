def page_graph():
    """
    Generate custom graphs to display sensor data retrieved from influxdb.
    """
    # Create form objects
    form_add_graph = flaskforms.GraphAdd()
    form_add_gauge = flaskforms.GaugeAdd()
    form_mod_graph = flaskforms.GraphMod()
    form_mod_gauge = flaskforms.GaugeMod()
    form_del_graph = flaskforms.GraphDel()
    form_order_graph = flaskforms.GraphOrder()

    # Retrieve the order to display graphs
    display_order = csv_to_list_of_int(DisplayOrder.query.first().graph)

    # Retrieve tables from SQL database
    graph = Graph.query.all()
    pid = PID.query.all()
    relay = Relay.query.all()
    sensor = Sensor.query.all()

    # Retrieve all choices to populate form drop-down menu
    pid_choices = flaskutils.choices_pids(pid)
    output_choices = flaskutils.choices_outputs(relay)
    sensor_choices = flaskutils.choices_sensors(sensor)

    # Add multi-select values as form choices, for validation
    form_mod_graph.pid_ids.choices = []
    form_mod_graph.relay_ids.choices = []
    form_mod_graph.sensor_ids.choices = []
    for key, value in pid_choices.items():
        form_mod_graph.pid_ids.choices.append((key, value))
    for key, value in output_choices.items():
        form_mod_graph.relay_ids.choices.append((key, value))
    for key, value in sensor_choices.items():
        form_mod_graph.sensor_ids.choices.append((key, value))

    # Generate dictionary of custom colors for each graph
    colors_graph = dict_custom_colors()

    # Retrieve custom colors for gauges
    colors_gauge = OrderedDict()
    for each_graph in graph:
        if each_graph.range_colors:  # Split into list
            color_areas = each_graph.range_colors.split(';')
        else:  # Create empty list
            color_areas = []
        total = []
        if each_graph.graph_type == 'gauge_angular':
            for each_range in color_areas:
                total.append({
                    'low': each_range.split(',')[0],
                    'high': each_range.split(',')[1],
                    'hex': each_range.split(',')[2]})
        elif each_graph.graph_type == 'gauge_solid':
            for each_range in color_areas:
                total.append({
                    'stop': each_range.split(',')[0],
                    'hex': each_range.split(',')[1]})
        colors_gauge.update({each_graph.id: total})

    # Detect which form on the page was submitted
    if request.method == 'POST':
        if not flaskutils.user_has_permission('edit_controllers'):
            return redirect(url_for('general_routes.home'))

        form_name = request.form['form-name']
        if form_name == 'modGraph':
            flaskutils.graph_mod(form_mod_graph, request.form)
        elif form_name == 'modGauge':
            flaskutils.graph_mod(form_mod_gauge, request.form)
        elif form_name == 'delGraph':
            flaskutils.graph_del(form_del_graph)
        elif form_order_graph.orderGraphUp.data:
            flaskutils.graph_reorder(form_order_graph.orderGraph_id.data,
                                     display_order, 'up')
        elif form_order_graph.orderGraphDown.data:
            flaskutils.graph_reorder(form_order_graph.orderGraph_id.data,
                                     display_order, 'down')
        elif form_name == 'addGraph':
            flaskutils.graph_add(form_add_graph, display_order)
        elif form_name == 'addGauge':
            flaskutils.graph_add(form_add_gauge, display_order)
        return redirect('/graph')

    return render_template('pages/graph.html',
                           graph=graph,
                           pid=pid,
                           relay=relay,
                           sensor=sensor,
                           pid_choices=pid_choices,
                           output_choices=output_choices,
                           sensor_choices=sensor_choices,
                           colors_graph=colors_graph,
                           colors_gauge=colors_gauge,
                           measurement_units=MEASUREMENT_UNITS,
                           displayOrder=display_order,
                           form_mod_graph=form_mod_graph,
                           form_mod_gauge=form_mod_gauge,
                           form_del_graph=form_del_graph,
                           form_order_graph=form_order_graph,
                           form_add_graph=form_add_graph,
                           form_add_gauge=form_add_gauge)