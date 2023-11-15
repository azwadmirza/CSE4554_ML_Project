def lst_avg(lst):
    '''
    Returns the average value of a list.

    .. code-block:: jinja

        {% my_list = [1,2,3,4] -%}
        {{ set my_list | avg }}

    will be rendered as:

    .. code-block:: yaml

        2.5
    '''
    if not isinstance(lst, collections.Hashable):
        return float(sum(lst)/len(lst))
    return float(lst)