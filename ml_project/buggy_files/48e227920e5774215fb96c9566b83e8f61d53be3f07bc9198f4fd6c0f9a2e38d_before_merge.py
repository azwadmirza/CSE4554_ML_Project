    def export_arrow(self, to, progress=None, chunk_size=default_chunk_size, parallel=True, reduce_large=True, fs_options=None):
        """Exports the DataFrame to a file of stream written with arrow

        :param to: filename, file object, or :py:data:`pyarrow.RecordBatchStreamWriter`, py:data:`pyarrow.RecordBatchFileWriter` or :py:data:`pyarrow.parquet.ParquetWriter`
        :param progress: {progress}
        :param int chunk_size: {chunk_size_export}
        :param bool parallel: {evaluate_parallel}
        :param bool reduce_large: If True, convert arrow large_string type to string type
        :param dict fs_options: Coming soon...
        :return:
        """
        progressbar = vaex.utils.progressbars(progress)
        def write(writer):
            progressbar(0)
            N = len(self)
            if chunk_size:
                for i1, i2, table in self.to_arrow_table(chunk_size=chunk_size, parallel=parallel, reduce_large=reduce_large):
                    writer.write_table(table)
                    progressbar(i2/N)
                progressbar(1.)
            else:
                table = self.to_arrow_table(chunk_size=chunk_size, parallel=parallel, reduce_large=reduce_large)
                writer.write_table(table)
        if isinstance(to, str):
            schema = self[0:1].to_arrow_table(parallel=False, reduce_large=reduce_large).schema
            fs_options = fs_options or {}
            with vaex.file.open_for_arrow(path=to, mode='wb', fs_options=fs_options) as sink:
                writer = pa.RecordBatchStreamWriter(sink, schema)
                write(writer)
        else:
            write(to)