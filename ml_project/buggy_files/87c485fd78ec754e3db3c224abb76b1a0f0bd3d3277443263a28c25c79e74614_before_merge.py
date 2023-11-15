    def __init__(self, obj, orient, date_format, double_precision,
                 ensure_ascii, date_unit, default_handler=None):
        """
        Adds a `schema` attribut with the Table Schema, resets
        the index (can't do in caller, because the schema inference needs
        to know what the index is, forces orient to records, and forces
        date_format to 'iso'.
        """
        super(JSONTableWriter, self).__init__(
            obj, orient, date_format, double_precision, ensure_ascii,
            date_unit, default_handler=default_handler)

        if date_format != 'iso':
            msg = ("Trying to write with `orient='table'` and "
                   "`date_format='%s'`. Table Schema requires dates "
                   "to be formatted with `date_format='iso'`" % date_format)
            raise ValueError(msg)

        self.schema = build_table_schema(obj)

        # TODO: Do this timedelta properly in objToJSON.c See GH #15137
        if ((obj.ndim == 1) and (obj.name in set(obj.index.names)) or
                len(obj.columns & obj.index.names)):
            msg = "Overlapping names between the index and columns"
            raise ValueError(msg)

        obj = obj.copy()
        timedeltas = obj.select_dtypes(include=['timedelta']).columns
        if len(timedeltas):
            obj[timedeltas] = obj[timedeltas].applymap(
                lambda x: x.isoformat())
        # Convert PeriodIndex to datetimes before serialzing
        if is_period_dtype(obj.index):
            obj.index = obj.index.to_timestamp()

        self.obj = obj.reset_index()
        self.date_format = 'iso'
        self.orient = 'records'