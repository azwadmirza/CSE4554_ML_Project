def process_dataframe_hierarchy(args):
    """
    Build dataframe for sunburst or treemap when the path argument is provided.
    """
    df = args["data_frame"]
    path = args["path"][::-1]
    _check_dataframe_all_leaves(df[path[::-1]])
    discrete_color = False

    new_path = []
    for col_name in path:
        new_col_name = col_name + "_path_copy"
        new_path.append(new_col_name)
        df[new_col_name] = df[col_name]
    path = new_path
    # ------------ Define aggregation functions --------------------------------

    def aggfunc_discrete(x):
        uniques = x.unique()
        if len(uniques) == 1:
            return uniques[0]
        else:
            return "(?)"

    agg_f = {}
    aggfunc_color = None
    if args["values"]:
        try:
            df[args["values"]] = pd.to_numeric(df[args["values"]])
        except ValueError:
            raise ValueError(
                "Column `%s` of `df` could not be converted to a numerical data type."
                % args["values"]
            )

        if args["color"]:
            if args["color"] == args["values"]:
                new_value_col_name = args["values"] + "_sum"
                df[new_value_col_name] = df[args["values"]]
                args["values"] = new_value_col_name
        count_colname = args["values"]
    else:
        # we need a count column for the first groupby and the weighted mean of color
        # trick to be sure the col name is unused: take the sum of existing names
        count_colname = (
            "count"
            if "count" not in df.columns
            else "".join([str(el) for el in list(df.columns)])
        )
        # we can modify df because it's a copy of the px argument
        df[count_colname] = 1
        args["values"] = count_colname
    agg_f[count_colname] = "sum"

    if args["color"]:
        if not _is_continuous(df, args["color"]):
            aggfunc_color = aggfunc_discrete
            discrete_color = True
        else:

            def aggfunc_continuous(x):
                return np.average(x, weights=df.loc[x.index, count_colname])

            aggfunc_color = aggfunc_continuous
        agg_f[args["color"]] = aggfunc_color

    #  Other columns (for color, hover_data, custom_data etc.)
    cols = list(set(df.columns).difference(path))
    for col in cols:  # for hover_data, custom_data etc.
        if col not in agg_f:
            agg_f[col] = aggfunc_discrete
    # Avoid collisions with reserved names - columns in the path have been copied already
    cols = list(set(cols) - set(["labels", "parent", "id"]))
    # ----------------------------------------------------------------------------
    df_all_trees = pd.DataFrame(columns=["labels", "parent", "id"] + cols)
    #  Set column type here (useful for continuous vs discrete colorscale)
    for col in cols:
        df_all_trees[col] = df_all_trees[col].astype(df[col].dtype)
    for i, level in enumerate(path):
        df_tree = pd.DataFrame(columns=df_all_trees.columns)
        dfg = df.groupby(path[i:]).agg(agg_f)
        dfg = dfg.reset_index()
        # Path label massaging
        df_tree["labels"] = dfg[level].copy().astype(str)
        df_tree["parent"] = ""
        df_tree["id"] = dfg[level].copy().astype(str)
        if i < len(path) - 1:
            j = i + 1
            while j < len(path):
                df_tree["parent"] = (
                    dfg[path[j]].copy().astype(str) + "/" + df_tree["parent"]
                )
                df_tree["id"] = dfg[path[j]].copy().astype(str) + "/" + df_tree["id"]
                j += 1

        df_tree["parent"] = df_tree["parent"].str.rstrip("/")
        if cols:
            df_tree[cols] = dfg[cols]
        df_all_trees = df_all_trees.append(df_tree, ignore_index=True)

    # we want to make sure than (?) is the first color of the sequence
    if args["color"] and discrete_color:
        sort_col_name = "sort_color_if_discrete_color"
        while sort_col_name in df_all_trees.columns:
            sort_col_name += "0"
        df_all_trees[sort_col_name] = df[args["color"]].astype(str)
        df_all_trees = df_all_trees.sort_values(by=sort_col_name)

    # Now modify arguments
    args["data_frame"] = df_all_trees
    args["path"] = None
    args["ids"] = "id"
    args["names"] = "labels"
    args["parents"] = "parent"
    if args["color"]:
        if not args["hover_data"]:
            args["hover_data"] = [args["color"]]
        elif isinstance(args["hover_data"], dict):
            if not args["hover_data"].get(args["color"]):
                args["hover_data"][args["color"]] = (True, None)
        else:
            args["hover_data"].append(args["color"])
    return args