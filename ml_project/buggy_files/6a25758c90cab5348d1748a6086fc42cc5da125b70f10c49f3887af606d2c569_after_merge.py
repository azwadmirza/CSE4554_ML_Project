    def to_excel(self, excel_writer, sheet_name='Sheet1', na_rep='',
                 float_format=None, columns=None, header=True, index=True,
                 index_label=None, startrow=0, startcol=0, engine=None,
                 merge_cells=True, encoding=None, inf_rep='inf'):
        """
        Write DataFrame to a excel sheet

        Parameters
        ----------
        excel_writer : string or ExcelWriter object
            File path or existing ExcelWriter
        sheet_name : string, default 'Sheet1'
            Name of sheet which will contain DataFrame
        na_rep : string, default ''
            Missing data representation
        float_format : string, default None
            Format string for floating point numbers
        columns : sequence, optional
            Columns to write
        header : boolean or list of string, default True
            Write out column names. If a list of string is given it is
            assumed to be aliases for the column names
        index : boolean, default True
            Write row names (index)
        index_label : string or sequence, default None
            Column label for index column(s) if desired. If None is given, and
            `header` and `index` are True, then the index names are used. A
            sequence should be given if the DataFrame uses MultiIndex.
        startrow :
            upper left cell row to dump data frame
        startcol :
            upper left cell column to dump data frame
        engine : string, default None
            write engine to use - you can also set this via the options
            ``io.excel.xlsx.writer``, ``io.excel.xls.writer``, and
            ``io.excel.xlsm.writer``.
        merge_cells : boolean, default True
            Write MultiIndex and Hierarchical Rows as merged cells.
        encoding: string, default None
            encoding of the resulting excel file. Only necessary for xlwt,
            other writers support unicode natively.
        inf_rep : string, default 'inf'
            Representation for infinity (there is no native representation for
            infinity in Excel)

        Notes
        -----
        If passing an existing ExcelWriter object, then the sheet will be added
        to the existing workbook.  This can be used to save different
        DataFrames to one workbook:

        >>> writer = ExcelWriter('output.xlsx')
        >>> df1.to_excel(writer,'Sheet1')
        >>> df2.to_excel(writer,'Sheet2')
        >>> writer.save()

        For compatibility with to_csv, to_excel serializes lists and dicts to
        strings before writing.
        """
        from pandas.io.excel import ExcelWriter
        if self.columns.nlevels > 1:
            raise NotImplementedError("Writing as Excel with a MultiIndex is "
                                      "not yet implemented.")

        need_save = False
        if encoding == None:
            encoding = 'ascii'

        if isinstance(excel_writer, compat.string_types):
            excel_writer = ExcelWriter(excel_writer, engine=engine)
            need_save = True

        formatter = fmt.ExcelFormatter(self,
                                       na_rep=na_rep,
                                       cols=columns,
                                       header=header,
                                       float_format=float_format,
                                       index=index,
                                       index_label=index_label,
                                       merge_cells=merge_cells,
                                       inf_rep=inf_rep)
        formatted_cells = formatter.get_formatted_cells()
        excel_writer.write_cells(formatted_cells, sheet_name,
                                 startrow=startrow, startcol=startcol)
        if need_save:
            excel_writer.save()