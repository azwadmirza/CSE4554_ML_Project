def _get_strategy_for_field(f):
    if f.choices:
        choices = []
        for value, name_or_optgroup in f.choices:
            if isinstance(name_or_optgroup, (list, tuple)):
                choices.extend(key for key, _ in name_or_optgroup)
            else:
                choices.append(value)
        if isinstance(f, (dm.CharField, dm.TextField)) and f.blank:
            choices.insert(0, u'')
        strategy = st.sampled_from(choices)
    elif type(f) == dm.SlugField:
        strategy = st.text(alphabet=string.ascii_letters + string.digits,
                           min_size=(None if f.blank else 1),
                           max_size=f.max_length)
    elif type(f) == dm.GenericIPAddressField:
        lookup = {'both': ip4_addr_strings() | ip6_addr_strings(),
                  'ipv4': ip4_addr_strings(), 'ipv6': ip6_addr_strings()}
        strategy = lookup[f.protocol.lower()]
    elif type(f) in (dm.TextField, dm.CharField):
        strategy = st.text(
            alphabet=st.characters(blacklist_characters=u'\x00',
                                   blacklist_categories=('Cs',)),
            min_size=(None if f.blank else 1),
            max_size=f.max_length,
        )
    elif type(f) == dm.DecimalField:
        bound = Decimal(10 ** f.max_digits - 1) / (10 ** f.decimal_places)
        strategy = st.decimals(min_value=-bound, max_value=bound,
                               places=f.decimal_places)
    else:
        strategy = field_mappings().get(type(f), st.nothing())
    if f.validators:
        strategy = strategy.filter(validator_to_filter(f))
    if f.null:
        strategy = st.one_of(st.none(), strategy)
    return strategy