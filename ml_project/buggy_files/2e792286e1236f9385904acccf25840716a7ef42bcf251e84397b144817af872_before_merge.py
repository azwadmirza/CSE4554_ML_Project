def generate_reports(report_template: Report, infile: BinaryIO, chunk_size: Optional[int],
                     copy_header_line: bool) -> Generator[Report, None, None]:
    """Generate reports from a template and input file, optionally split into chunks.

    If chunk_size is None, a single report is generated with the entire
    contents of infile as the raw data. Otherwise chunk_size should be
    an integer giving the maximum number of bytes in a chunk. The data
    read from infile is then split into chunks of this size at newline
    characters (see read_delimited_chunks). For each of the chunks, this
    function yields a copy of the report_template with that chunk as the
    value of the raw attribute.

    When splitting the data into chunks, if copy_header_line is true,
    the first line the file is read before chunking and then prepended
    to each of the chunks. This is particularly useful when splitting
    CSV files.

    The infile should be a file-like object. generate_reports uses only
    two methods, readline and read, with readline only called once and
    only if copy_header_line is true. Both methods should return bytes
    objects.

    Params:
        report_template: report used as template for all yielded copies
        infile: stream to read from
        chunk_size: maximum size of each chunk
        copy_header_line: copy the first line of the infile to each chunk

    Yields:
        report: a Report object holding the chunk in the raw field
    """
    if chunk_size is None:
        report = report_template.copy()
        report.add("raw", infile.read(), overwrite=True)
        yield report
    else:
        header = b""
        if copy_header_line:
            header = infile.readline()
        for chunk in read_delimited_chunks(infile, chunk_size):
            report = report_template.copy()
            report.add("raw", header + chunk, overwrite=True)
            yield report