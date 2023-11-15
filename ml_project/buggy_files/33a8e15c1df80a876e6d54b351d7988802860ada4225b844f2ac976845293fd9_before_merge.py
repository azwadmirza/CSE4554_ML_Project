    def transform_joinaggregate(self, joinaggregate=Undefined, groupby=Undefined, **kwargs):
        """
        Add a JoinAggregateTransform to the schema.

        Parameters
        ----------
        joinaggregate : List(:class:`JoinAggregateFieldDef`)
            The definition of the fields in the join aggregate, and what calculations to use.
        groupby : List(string)
            The data fields for partitioning the data objects into separate groups. If
            unspecified, all data points will be in a single group.
        **kwargs
            joinaggregates can also be passed by keyword argument; see Examples.

        Returns
        -------
        self : Chart object
            returns chart to allow for chaining

        Examples
        --------
        >>> import altair as alt
        >>> chart = alt.Chart().transform_joinaggregate(x='sum(y)')
        >>> chart.transform[0]
        JoinAggregateTransform({
          joinaggregate: [JoinAggregateFieldDef({
            as: FieldName('x'),
            field: FieldName('y'),
            op: AggregateOp('sum')
          })]
        })

        See Also
        --------
        alt.JoinAggregateTransform : underlying transform object
        """
        if joinaggregate is Undefined:
            joinaggregate = []
        for key, val in kwargs.items():
            parsed = utils.parse_shorthand(val)
            dct = {'as': key,
                   'field': parsed.get('field', Undefined),
                   'op': parsed.get('aggregate', Undefined)}
            joinaggregate.append(core.JoinAggregateFieldDef.from_dict(dct))
        return self._add_transform(core.JoinAggregateTransform(
            joinaggregate=joinaggregate, groupby=groupby
        ))