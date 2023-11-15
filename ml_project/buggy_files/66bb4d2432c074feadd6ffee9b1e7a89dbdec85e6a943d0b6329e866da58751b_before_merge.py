def _add_margins(table, data, values, rows, cols, aggfunc):

    grand_margin = _compute_grand_margin(data, values, aggfunc)

    if not values and isinstance(table, Series):
        # If there are no values and the table is a series, then there is only
        # one column in the data. Compute grand margin and return it.
        row_key = ('All',) + ('',) * (len(rows) - 1) if len(rows) > 1 else 'All'
        return table.append(Series({row_key: grand_margin['All']}))

    if values:
        marginal_result_set = _generate_marginal_results(table, data, values, rows, cols, aggfunc, grand_margin)
        if not isinstance(marginal_result_set, tuple):
            return marginal_result_set
        result, margin_keys, row_margin = marginal_result_set
    else:
        marginal_result_set = _generate_marginal_results_without_values(table, data, rows, cols, aggfunc)
        if not isinstance(marginal_result_set, tuple):
            return marginal_result_set
        result, margin_keys, row_margin = marginal_result_set

    key = ('All',) + ('',) * (len(rows) - 1) if len(rows) > 1 else 'All'

    row_margin = row_margin.reindex(result.columns)
    # populate grand margin
    for k in margin_keys:
        if isinstance(k, compat.string_types):
            row_margin[k] = grand_margin[k]
        else:
            row_margin[k] = grand_margin[k[0]]

    margin_dummy = DataFrame(row_margin, columns=[key]).T

    row_names = result.index.names
    result = result.append(margin_dummy)
    result.index.names = row_names

    return result