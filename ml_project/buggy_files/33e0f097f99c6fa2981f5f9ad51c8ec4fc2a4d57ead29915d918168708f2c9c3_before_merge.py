    def _range_filter_to_indicator(filter, col, fmin, fmax):
        if filter.oper == filter.Equal:
            return col == fmin
        if filter.oper == filter.NotEqual:
            return col != fmin
        if filter.oper == filter.Less:
            return col < fmin
        if filter.oper == filter.LessEqual:
            return col <= fmin
        if filter.oper == filter.Greater:
            return col > fmin
        if filter.oper == filter.GreaterEqual:
            return col >= fmin
        if filter.oper == filter.Between:
            return (col >= fmin) * (col <= fmax)
        if filter.oper == filter.Outside:
            return (col < fmin) + (col > fmax)

        raise TypeError("Invalid operator")