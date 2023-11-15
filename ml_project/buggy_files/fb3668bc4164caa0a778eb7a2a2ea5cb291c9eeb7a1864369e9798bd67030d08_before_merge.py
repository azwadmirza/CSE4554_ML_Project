    def __inspect_table(self, table):

        # Start timer
        start = datetime.datetime.now()

        # Prepare vars
        errors = []
        headers = None
        row_number = 0
        fatal_error = False
        checks = copy(self.__checks)
        source = table['source']
        stream = table['stream']
        schema = table['schema']
        extra = table['extra']

        # Prepare table
        try:
            stream.open()
            sample = stream.sample
            headers = stream.headers
            if self.__filter_checks(checks, type='schema'):
                if schema is None and self.__infer_schema:
                    schema = Schema(infer(headers, sample))
            if schema is None:
                checks = self.__filter_checks(checks, type='schema', inverse=True)
        except Exception as exception:
            fatal_error = True
            message = str(exception)
            if isinstance(exception, tabulator.exceptions.SourceError):
                code = 'source-error'
            elif isinstance(exception, tabulator.exceptions.SchemeError):
                code = 'scheme-error'
            elif isinstance(exception, tabulator.exceptions.FormatError):
                code = 'format-error'
            elif isinstance(exception, tabulator.exceptions.EncodingError):
                code = 'encoding-error'
            elif isinstance(exception, tabulator.exceptions.IOError):
                code = 'io-error'
            elif isinstance(exception, tabulator.exceptions.HTTPError):
                code = 'http-error'
            else:
                raise
            errors.append({
                'row': None,
                'code': code,
                'message': message,
                'row-number': None,
                'column-number': None,
            })

        # Prepare columns
        if not fatal_error:
            columns = []
            fields = [None] * len(headers)
            if schema is not None:
                fields = schema.fields
            iterator = zip_longest(headers, fields, fillvalue=_FILLVALUE)
            for number, (header, field) in enumerate(iterator, start=1):
                column = {'number': number}
                if header is not _FILLVALUE:
                    column['header'] = header
                if field is not _FILLVALUE:
                    column['field'] = field
                columns.append(column)

        # Head checks
        if not fatal_error:
            head_checks = self.__filter_checks(checks, context='head')
            for check in head_checks:
                if not columns:
                    break
                check['func'](errors, columns, sample)
            for error in errors:
                error['row'] = None

        # Body checks
        if not fatal_error:
            states = {}
            colmap = {column['number']: column for column in columns}
            body_checks = self.__filter_checks(checks, context='body')
            with stream:
                for row_number, headers, row in stream.iter(extended=True):
                    columns = []
                    iterator = zip_longest(headers, row, fillvalue=_FILLVALUE)
                    for number, (header, value) in enumerate(iterator, start=1):
                        colref = colmap.get(number, {})
                        column = {'number': number}
                        if header is not _FILLVALUE:
                            column['header'] = colref.get('header', header)
                        if 'field' in colref:
                            column['field'] = colref['field']
                        if value is not _FILLVALUE:
                            column['value'] = value
                        columns.append(column)
                    for check in body_checks:
                        if not columns:
                            break
                        state = states.setdefault(check['code'], {})
                        check['func'](errors, columns, row_number, state)
                    for error in reversed(errors):
                        if 'row' in error:
                            break
                        error['row'] = row
                    if row_number >= self.__row_limit:
                        break
                    if len(errors) >= self.__error_limit:
                        break

        # Stop timer
        stop = datetime.datetime.now()

        # Compose report
        errors = errors[:self.__error_limit]
        report = copy(extra)
        report.update({
            'time': round((stop - start).total_seconds(), 3),
            'valid': not bool(errors),
            'error-count': len(errors),
            'row-count': row_number,
            'headers': headers,
            'source': source,
            'errors': errors,
        })

        return report