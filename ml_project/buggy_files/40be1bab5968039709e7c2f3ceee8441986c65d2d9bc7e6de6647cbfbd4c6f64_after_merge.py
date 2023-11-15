    def _parse_excel(self, sheetname=0, header=0, skiprows=None, skip_footer=0,
                     index_col=None, has_index_names=None, parse_cols=None,
                     parse_dates=False, date_parser=None, na_values=None,
                     thousands=None, chunksize=None, convert_float=True,
                     verbose=False, **kwds):
        import xlrd
        from xlrd import (xldate, XL_CELL_DATE,
                          XL_CELL_ERROR, XL_CELL_BOOLEAN,
                          XL_CELL_NUMBER)

        epoch1904 = self.book.datemode

        def _parse_cell(cell_contents,cell_typ):
            """converts the contents of the cell into a pandas
               appropriate object"""
               
            if cell_typ == XL_CELL_DATE:
                if xlrd_0_9_3:
                    # Use the newer xlrd datetime handling.
                    cell_contents = xldate.xldate_as_datetime(cell_contents,
                                                              epoch1904)

                    # Excel doesn't distinguish between dates and time,
                    # so we treat dates on the epoch as times only.
                    # Also, Excel supports 1900 and 1904 epochs.
                    year = (cell_contents.timetuple())[0:3]
                    if ((not epoch1904 and year == (1899, 12, 31))
                            or (epoch1904 and year == (1904, 1, 1))):
                        cell_contents = datetime.time(cell_contents.hour,
                                              cell_contents.minute,
                                              cell_contents.second,
                                              cell_contents.microsecond)
                else:
                    # Use the xlrd <= 0.9.2 date handling.
                    dt = xldate.xldate_as_tuple(cell_contents, epoch1904)

                    if dt[0] < datetime.MINYEAR:
                        cell_contents = datetime.time(*dt[3:])
                    else:
                        cell_contents = datetime.datetime(*dt)

            elif cell_typ == XL_CELL_ERROR:
                cell_contents = np.nan
            elif cell_typ == XL_CELL_BOOLEAN:
                cell_contents = bool(cell_contents)
            elif convert_float and cell_typ == XL_CELL_NUMBER:
                # GH5394 - Excel 'numbers' are always floats
                # it's a minimal perf hit and less suprising
                val = int(cell_contents)
                if val == cell_contents:
                    cell_contents = val
            return cell_contents

        # xlrd >= 0.9.3 can return datetime objects directly.
        if LooseVersion(xlrd.__VERSION__) >= LooseVersion("0.9.3"):
            xlrd_0_9_3 = True
        else:
            xlrd_0_9_3 = False
        
        ret_dict = False
        
        #Keep sheetname to maintain backwards compatibility.
        if isinstance(sheetname, list):
            sheets = sheetname
            ret_dict = True
        elif sheetname is None:
            sheets = self.sheet_names
            ret_dict = True
        else:
            sheets = [sheetname]
        
        #handle same-type duplicates.
        sheets = list(set(sheets))
        
        output = {}
        
        for asheetname in sheets:
            if verbose:
                print("Reading sheet %s" % asheetname)
            
            if isinstance(asheetname, compat.string_types):
                sheet = self.book.sheet_by_name(asheetname)
            else:  # assume an integer if not a string    
                sheet = self.book.sheet_by_index(asheetname)   
            
            data = []
            should_parse = {}
            
            for i in range(sheet.nrows):
                row = []
                for j, (value, typ) in enumerate(zip(sheet.row_values(i),
                                                     sheet.row_types(i))):
                    if parse_cols is not None and j not in should_parse:
                        should_parse[j] = self._should_parse(j, parse_cols)
    
                    if parse_cols is None or should_parse[j]:
                        row.append(_parse_cell(value,typ))
                data.append(row)

            if sheet.nrows == 0:
                return DataFrame()

            if header is not None:
                data[header] = _trim_excel_header(data[header])

            parser = TextParser(data, header=header, index_col=index_col,
                                has_index_names=has_index_names,
                                na_values=na_values,
                                thousands=thousands,
                                parse_dates=parse_dates,
                                date_parser=date_parser,
                                skiprows=skiprows,
                                skip_footer=skip_footer,
                                chunksize=chunksize,
                                **kwds)
            
            output[asheetname] = parser.read()
            
        if ret_dict:
            return output
        else:
            return output[asheetname]