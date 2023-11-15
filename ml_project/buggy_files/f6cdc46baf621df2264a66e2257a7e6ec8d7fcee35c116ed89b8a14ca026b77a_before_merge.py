def percentileRank(frame, column=None, kind='mean'):
    """
    Return score at percentile for each point in time (cross-section)

    Parameters
    ----------
    frame: DataFrame
    column: string or Series, optional
       Column name or specific Series to compute percentiles for.
       If not provided, percentiles are computed for all values at each
       point in time. Note that this can take a LONG time.
    kind: {'rank', 'weak', 'strict', 'mean'}, optional
        This optional parameter specifies the interpretation of the
        resulting score:

        - "rank": Average percentage ranking of score.  In case of
                  multiple matches, average the percentage rankings of
                  all matching scores.
        - "weak": This kind corresponds to the definition of a cumulative
                  distribution function.  A percentileofscore of 80%
                  means that 80% of values are less than or equal
                  to the provided score.
        - "strict": Similar to "weak", except that only values that are
                    strictly less than the given score are counted.
        - "mean": The average of the "weak" and "strict" scores, often used in
                  testing.  See

                  http://en.wikipedia.org/wiki/Percentile_rank

    See also
    --------
    scipy.stats.percentileofscore

    Returns
    -------
    TimeSeries or DataFrame, depending on input
    """
    from scipy.stats import percentileofscore
    fun = lambda xs, score: percentileofscore(remove_na(xs),
                                              score, kind=kind)

    results = {}
    framet = frame.T
    if column is not None:
        if isinstance(column, Series):
            for date, xs in frame.T.iteritems():
                results[date] = fun(xs, column.get(date, NaN))
        else:
            for date, xs in frame.T.iteritems():
                results[date] = fun(xs, xs[column])
        results = Series(results)
    else:
        for column in frame.columns:
            for date, xs in framet.iteritems():
                results.setdefault(date, {})[column] = fun(xs, xs[column])
        results = DataFrame(results).T
    return results