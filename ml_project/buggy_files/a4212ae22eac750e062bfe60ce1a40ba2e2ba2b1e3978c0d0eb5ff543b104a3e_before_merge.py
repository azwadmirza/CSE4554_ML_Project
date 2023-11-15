            def sort_index_for_equal_values(result, ascending):
                """
                Sort indices for equal values of result object.

                Parameters
                ----------
                result : pandas.Series or pandas.DataFrame with one column
                    The object whose indices for equal values is needed to sort.
                ascending : boolean
                    Sort in ascending (if it is True) or descending (if it is False) order.

                Returns
                -------
                pandas.DataFrame
                    A new DataFrame with sorted indices.
                """
                is_range = False
                is_end = False
                i = 0
                new_index = np.empty(len(result), dtype=type(result.index))
                while i < len(result):
                    j = i
                    if i < len(result) - 1:
                        while result[result.index[i]] == result[result.index[i + 1]]:
                            i += 1
                            if is_range is False:
                                is_range = True
                            if i == len(result) - 1:
                                is_end = True
                                break
                    if is_range:
                        k = j
                        for val in sorted(
                            result.index[j : i + 1], reverse=not ascending
                        ):
                            new_index[k] = val
                            k += 1
                        if is_end:
                            break
                        is_range = False
                    else:
                        new_index[j] = result.index[j]
                    i += 1
                return pandas.DataFrame(result, index=new_index)