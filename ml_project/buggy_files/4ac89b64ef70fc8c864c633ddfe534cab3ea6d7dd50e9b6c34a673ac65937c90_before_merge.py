def compute_univariate(
    df: dd.DataFrame,
    x: str,
    bins: int,
    ngroups: int,
    largest: bool,
    timeunit: str,
    value_range: Optional[Tuple[float, float]] = None,
    dtype: Optional[DTypeDef] = None,
    top_words: Optional[int] = 30,
    stopword: Optional[bool] = True,
    lemmatize: Optional[bool] = False,
    stem: Optional[bool] = False,
) -> Intermediate:
    """
    Compute functions for plot(df, x)
    Parameters
    ----------
    df
        Dataframe from which plots are to be generated
    x
        A valid column name from the dataframe
    bins
        For a histogram or box plot with numerical x axis, it defines
        the number of equal-width bins to use when grouping.
    ngroups
        When grouping over a categorical column, it defines the
        number of groups to show in the plot. Ie, the number of
        bars to show in a bar chart.
    largest
        If true, when grouping over a categorical column, the groups
        with the largest count will be output. If false, the groups
        with the smallest count will be output.
    timeunit
        Defines the time unit to group values over for a datetime column.
        It can be "year", "quarter", "month", "week", "day", "hour",
        "minute", "second". With default value "auto", it will use the
        time unit such that the resulting number of groups is closest to 15.
    value_range
        The lower and upper bounds on the range of a numerical column.
        Applies when column x is specified and column y is unspecified.
    dtype: str or DType or dict of str or dict of DType, default None
        Specify Data Types for designated column or all columns.
        E.g.  dtype = {"a": Continuous, "b": "Nominal"} or
        dtype = {"a": Continuous(), "b": "nominal"}
        or dtype = Continuous() or dtype = "Continuous" or dtype = Continuous()
    top_words: int, default 30
        Specify the amount of words to show in the wordcloud and
        word frequency bar chart
    stopword: bool, default True
        Eliminate the stopwords in the text data for plotting wordcloud and
        word frequency bar chart
    lemmatize: bool, default False
        Lemmatize the words in the text data for plotting wordcloud and
        word frequency bar chart
    stem: bool, default False
        Apply Potter Stem on the text data for plotting wordcloud and
        word frequency bar chart
    """
    # pylint: disable=too-many-locals, too-many-arguments

    col_dtype = detect_dtype(df[x], dtype)
    if is_dtype(col_dtype, Nominal()):
        # data for bar and pie charts
        data_cat: List[Any] = []
        data_cat.append(dask.delayed(calc_bar_pie)(df[x], ngroups, largest))
        # stats
        data_cat.append(dask.delayed(calc_stats_cat)(df[x]))
        data, statsdata_cat = dask.compute(*data_cat)

        # wordcloud and word frequencies
        word_cloud = cal_word_freq(df, x, top_words, stopword, lemmatize, stem)
        # length_distribution
        length_dist = cal_length_dist(df, x, bins)
        return Intermediate(
            col=x,
            data=data,
            statsdata=statsdata_cat,
            word_cloud=word_cloud,
            length_dist=length_dist,
            visual_type="categorical_column",
        )
    elif is_dtype(col_dtype, Continuous()):
        if value_range is not None:
            if (
                (value_range[0] <= np.nanmax(df[x]))
                and (value_range[1] >= np.nanmin(df[x]))
                and (value_range[0] < value_range[1])
            ):
                df = df[df[x].between(value_range[0], value_range[1])]
            else:
                print("Invalid range of values for this column", file=stderr)
        data_num: List[Any] = []
        # qq plot
        qqdata = calc_qqnorm(df[x].dropna())
        # kde plot
        kdedata = calc_hist_kde(df[x].dropna().values, bins)
        # box plot
        boxdata = calc_box(df[[x]].dropna(), bins, dtype=dtype)
        # histogram
        data_num.append(dask.delayed(calc_hist)(df[x], bins))
        # stats
        data_num.append(
            dask.delayed(calc_stats_num)(
                df[x],
                mean=qqdata[2],
                std=qqdata[3],
                min=kdedata[3],
                max=kdedata[4],
                quantile=qqdata[0],
            )
        )
        histdata, statsdata_num = dask.compute(*data_num)
        return Intermediate(
            col=x,
            histdata=histdata,
            kdedata=kdedata,
            qqdata=qqdata,
            boxdata=boxdata,
            statsdata=statsdata_num,
            visual_type="numerical_column",
        )
    elif is_dtype(col_dtype, DateTime()):
        data_dt: List[Any] = []
        # line chart
        data_dt.append(dask.delayed(calc_line_dt)(df[[x]], timeunit))
        # stats
        data_dt.append(dask.delayed(calc_stats_dt)(df[x]))
        data, statsdata_dt = dask.compute(*data_dt)
        return Intermediate(
            col=x, data=data, statsdata=statsdata_dt, visual_type="datetime_column",
        )
    else:
        raise UnreachableError