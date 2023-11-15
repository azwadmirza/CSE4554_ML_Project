def interestingness(vis: Vis, ldf: LuxDataFrame) -> int:
    """
    Compute the interestingness score of the vis.
    The interestingness metric is dependent on the vis type.

    Parameters
    ----------
    vis : Vis
    ldf : LuxDataFrame

    Returns
    -------
    int
            Interestingness Score
    """

    if vis.data is None or len(vis.data) == 0:
        return -1
        # raise Exception("Vis.data needs to be populated before interestingness can be computed. Run Executor.execute(vis,ldf).")

    n_dim = 0
    n_msr = 0

    filter_specs = utils.get_filter_specs(vis._inferred_intent)
    vis_attrs_specs = utils.get_attrs_specs(vis._inferred_intent)

    record_attrs = list(
        filter(
            lambda x: x.attribute == "Record" and x.data_model == "measure",
            vis_attrs_specs,
        )
    )
    n_record = len(record_attrs)
    for clause in vis_attrs_specs:
        if clause.attribute != "Record":
            if clause.data_model == "dimension":
                n_dim += 1
            if clause.data_model == "measure":
                n_msr += 1
    n_filter = len(filter_specs)
    attr_specs = [clause for clause in vis_attrs_specs if clause.attribute != "Record"]
    dimension_lst = vis.get_attr_by_data_model("dimension")
    measure_lst = vis.get_attr_by_data_model("measure")
    v_size = len(vis.data)

    if (
        n_dim == 1
        and (n_msr == 0 or n_msr == 1)
        and ldf.current_vis is not None
        and vis.get_attr_by_channel("y")[0].data_type == "quantitative"
        and len(ldf.current_vis) == 1
        and ldf.current_vis[0].mark == "line"
        and len(get_filter_specs(ldf.intent)) > 0
    ):
        query_vc = VisList(ldf.current_vis, ldf)
        query_vis = query_vc[0]
        preprocess(query_vis)
        preprocess(vis)
        return 1 - euclidean_dist(query_vis, vis)

    # Line/Bar Chart
    # print("r:", n_record, "m:", n_msr, "d:",n_dim)
    if n_dim == 1 and (n_msr == 0 or n_msr == 1):
        if v_size < 2:
            return -1

        if n_filter == 0:
            return unevenness(vis, ldf, measure_lst, dimension_lst)
        elif n_filter == 1:
            return deviation_from_overall(vis, ldf, filter_specs, measure_lst[0].attribute)
    # Histogram
    elif n_dim == 0 and n_msr == 1:
        if v_size < 2:
            return -1
        if n_filter == 0 and "Number of Records" in vis.data:
            if "Number of Records" in vis.data:
                v = vis.data["Number of Records"]
                return skewness(v)
        elif n_filter == 1 and "Number of Records" in vis.data:
            return deviation_from_overall(vis, ldf, filter_specs, "Number of Records")
        return -1
    # Scatter Plot
    elif n_dim == 0 and n_msr == 2:
        if v_size < 10:
            return -1
        if vis.mark == "heatmap":
            return weighted_correlation(vis.data["xBinStart"], vis.data["yBinStart"], vis.data["count"])
        if n_filter == 1:
            v_filter_size = get_filtered_size(filter_specs, vis.data)
            sig = v_filter_size / v_size
        else:
            sig = 1
        return sig * monotonicity(vis, attr_specs)
    # Scatterplot colored by Dimension
    elif n_dim == 1 and n_msr == 2:
        if v_size < 10:
            return -1
        color_attr = vis.get_attr_by_channel("color")[0].attribute

        C = ldf.cardinality[color_attr]
        if C < 40:
            return 1 / C
        else:
            return -1
    # Scatterplot colored by dimension
    elif n_dim == 1 and n_msr == 2:
        return 0.2
    # Scatterplot colored by measure
    elif n_msr == 3:
        return 0.1
    # colored line and barchart cases
    elif vis.mark == "line" and n_dim == 2:
        return 0.15
    # for colored bar chart, scoring based on Chi-square test for independence score.
    # gives higher scores to colored bar charts with fewer total categories as these charts are easier to read and thus more useful for users
    elif vis.mark == "bar" and n_dim == 2:
        from scipy.stats import chi2_contingency

        measure_column = vis.get_attr_by_data_model("measure")[0].attribute
        dimension_columns = vis.get_attr_by_data_model("dimension")

        groupby_column = dimension_columns[0].attribute
        color_column = dimension_columns[1].attribute

        contingency_table = []
        groupby_cardinality = ldf.cardinality[groupby_column]
        groupby_unique_vals = ldf.unique_values[groupby_column]
        for c in range(0, groupby_cardinality):
            contingency_table.append(
                vis.data[vis.data[groupby_column] == groupby_unique_vals[c]][measure_column]
            )
        score = 0.12
        # ValueError results if an entire column of the contingency table is 0, can happen if an applied filter results in
        # a category having no counts

        try:
            color_cardinality = ldf.cardinality[color_column]
            # scale down score based on number of categories
            chi2_score = chi2_contingency(contingency_table)[0] * 0.9 ** (
                color_cardinality + groupby_cardinality
            )
            score = min(0.10, chi2_score)
        except ValueError:
            pass
        return score
    # Default
    else:
        return -1