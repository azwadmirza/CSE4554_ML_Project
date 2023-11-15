def guess_ext(fname, sniff_order, is_binary=False):
    """
    Returns an extension that can be used in the datatype factory to
    generate a data for the 'fname' file

    >>> from galaxy.datatypes.registry import example_datatype_registry_for_sample
    >>> datatypes_registry = example_datatype_registry_for_sample()
    >>> sniff_order = datatypes_registry.sniff_order
    >>> fname = get_test_fname('megablast_xml_parser_test1.blastxml')
    >>> guess_ext(fname, sniff_order)
    'blastxml'
    >>> fname = get_test_fname('interval.interval')
    >>> guess_ext(fname, sniff_order)
    'interval'
    >>> fname = get_test_fname('interval1.bed')
    >>> guess_ext(fname, sniff_order)
    'bed'
    >>> fname = get_test_fname('test_tab.bed')
    >>> guess_ext(fname, sniff_order)
    'bed'
    >>> fname = get_test_fname('sequence.maf')
    >>> guess_ext(fname, sniff_order)
    'maf'
    >>> fname = get_test_fname('sequence.fasta')
    >>> guess_ext(fname, sniff_order)
    'fasta'
    >>> fname = get_test_fname('1.genbank')
    >>> guess_ext(fname, sniff_order)
    'genbank'
    >>> fname = get_test_fname('1.genbank.gz')
    >>> guess_ext(fname, sniff_order)
    'genbank.gz'
    >>> fname = get_test_fname('file.html')
    >>> guess_ext(fname, sniff_order)
    'html'
    >>> fname = get_test_fname('test.gtf')
    >>> guess_ext(fname, sniff_order)
    'gtf'
    >>> fname = get_test_fname('test.gff')
    >>> guess_ext(fname, sniff_order)
    'gff'
    >>> fname = get_test_fname('gff_version_3.gff')
    >>> guess_ext(fname, sniff_order)
    'gff3'
    >>> fname = get_test_fname('2.txt')
    >>> guess_ext(fname, sniff_order)  # 2.txt
    'txt'
    >>> fname = get_test_fname('2.tabular')
    >>> guess_ext(fname, sniff_order)
    'tabular'
    >>> fname = get_test_fname('3.txt')
    >>> guess_ext(fname, sniff_order)  # 3.txt
    'txt'
    >>> fname = get_test_fname('test_tab1.tabular')
    >>> guess_ext(fname, sniff_order)
    'tabular'
    >>> fname = get_test_fname('alignment.lav')
    >>> guess_ext(fname, sniff_order)
    'lav'
    >>> fname = get_test_fname('1.sff')
    >>> guess_ext(fname, sniff_order)
    'sff'
    >>> fname = get_test_fname('1.bam')
    >>> guess_ext(fname, sniff_order)
    'bam'
    >>> fname = get_test_fname('3unsorted.bam')
    >>> guess_ext(fname, sniff_order)
    'unsorted.bam'
    >>> fname = get_test_fname('test.idpDB')
    >>> guess_ext(fname, sniff_order)
    'idpdb'
    >>> fname = get_test_fname('test.mz5')
    >>> guess_ext(fname, sniff_order)
    'h5'
    >>> fname = get_test_fname('issue1818.tabular')
    >>> guess_ext(fname, sniff_order)
    'tabular'
    >>> fname = get_test_fname('drugbank_drugs.cml')
    >>> guess_ext(fname, sniff_order)
    'cml'
    >>> fname = get_test_fname('q.fps')
    >>> guess_ext(fname, sniff_order)
    'fps'
    >>> fname = get_test_fname('drugbank_drugs.inchi')
    >>> guess_ext(fname, sniff_order)
    'inchi'
    >>> fname = get_test_fname('drugbank_drugs.mol2')
    >>> guess_ext(fname, sniff_order)
    'mol2'
    >>> fname = get_test_fname('drugbank_drugs.sdf')
    >>> guess_ext(fname, sniff_order)
    'sdf'
    >>> fname = get_test_fname('5e5z.pdb')
    >>> guess_ext(fname, sniff_order)
    'pdb'
    >>> fname = get_test_fname('mothur_datatypetest_true.mothur.otu')
    >>> guess_ext(fname, sniff_order)
    'mothur.otu'
    >>> fname = get_test_fname('mothur_datatypetest_true.mothur.lower.dist')
    >>> guess_ext(fname, sniff_order)
    'mothur.lower.dist'
    >>> fname = get_test_fname('mothur_datatypetest_true.mothur.square.dist')
    >>> guess_ext(fname, sniff_order)
    'mothur.square.dist'
    >>> fname = get_test_fname('mothur_datatypetest_true.mothur.pair.dist')
    >>> guess_ext(fname, sniff_order)
    'mothur.pair.dist'
    >>> fname = get_test_fname('mothur_datatypetest_true.mothur.freq')
    >>> guess_ext(fname, sniff_order)
    'mothur.freq'
    >>> fname = get_test_fname('mothur_datatypetest_true.mothur.quan')
    >>> guess_ext(fname, sniff_order)
    'mothur.quan'
    >>> fname = get_test_fname('mothur_datatypetest_true.mothur.ref.taxonomy')
    >>> guess_ext(fname, sniff_order)
    'mothur.ref.taxonomy'
    >>> fname = get_test_fname('mothur_datatypetest_true.mothur.axes')
    >>> guess_ext(fname, sniff_order)
    'mothur.axes'
    >>> guess_ext(get_test_fname('infernal_model.cm'), sniff_order)
    'cm'
    >>> fname = get_test_fname('1.gg')
    >>> guess_ext(fname, sniff_order)
    'gg'
    >>> fname = get_test_fname('diamond_db.dmnd')
    >>> guess_ext(fname, sniff_order)
    'dmnd'
    >>> fname = get_test_fname('1.xls')
    >>> guess_ext(fname, sniff_order)
    'excel.xls'
    >>> fname = get_test_fname('biom2_sparse_otu_table_hdf5.biom')
    >>> guess_ext(fname, sniff_order)
    'biom2'
    >>> fname = get_test_fname('454Score.pdf')
    >>> guess_ext(fname, sniff_order)
    'pdf'
    >>> fname = get_test_fname('1.obo')
    >>> guess_ext(fname, sniff_order)
    'obo'
    >>> fname = get_test_fname('1.arff')
    >>> guess_ext(fname, sniff_order)
    'arff'
    >>> fname = get_test_fname('1.afg')
    >>> guess_ext(fname, sniff_order)
    'afg'
    >>> fname = get_test_fname('1.owl')
    >>> guess_ext(fname, sniff_order)
    'owl'
    >>> fname = get_test_fname('Acanium.hmm')
    >>> guess_ext(fname, sniff_order)
    'snaphmm'
    >>> fname = get_test_fname('wiggle.wig')
    >>> guess_ext(fname, sniff_order)
    'wig'
    >>> fname = get_test_fname('example.iqtree')
    >>> guess_ext(fname, sniff_order)
    'iqtree'
    >>> fname = get_test_fname('1.stockholm')
    >>> guess_ext(fname, sniff_order)
    'stockholm'
    >>> fname = get_test_fname('1.xmfa')
    >>> guess_ext(fname, sniff_order)
    'xmfa'
    >>> fname = get_test_fname('test.blib')
    >>> guess_ext(fname, sniff_order)
    'blib'
    >>> fname = get_test_fname('test.phylip')
    >>> guess_ext(fname, sniff_order)
    'phylip'
    >>> fname = get_test_fname('1.smat')
    >>> guess_ext(fname, sniff_order)
    'smat'
    >>> fname = get_test_fname('1.ttl')
    >>> guess_ext(fname, sniff_order)
    'ttl'
    >>> fname = get_test_fname('1.hdt')
    >>> guess_ext(fname, sniff_order)
    'hdt'
    >>> fname = get_test_fname('1.phyloxml')
    >>> guess_ext(fname, sniff_order)
    'phyloxml'
    >>> fname = get_test_fname('1.tiff')
    >>> guess_ext(fname, sniff_order)
    'tiff'
    >>> fname = get_test_fname('1.fastqsanger.gz')
    >>> guess_ext(fname, sniff_order)  # See test_datatype_registry for more compressed type tests.
    'fastqsanger.gz'
    """
    file_prefix = FilePrefix(fname)
    file_ext = run_sniffers_raw(file_prefix, sniff_order, is_binary)

    # Ugly hack for tsv vs tabular sniffing, we want to prefer tabular
    # to tsv but it doesn't have a sniffer - is TSV was sniffed just check
    # if it is an okay tabular and use that instead.
    if file_ext == 'tsv':
        if is_column_based(file_prefix, '\t', 1):
            file_ext = 'tabular'
    if file_ext is not None:
        return file_ext

    # skip header check if data is already known to be binary
    if is_binary:
        return file_ext or 'binary'
    try:
        get_headers(file_prefix, None)
    except UnicodeDecodeError:
        return 'data'  # default data type file extension
    if is_column_based(file_prefix, '\t', 1):
        return 'tabular'  # default tabular data type file extension
    return 'txt'  # default text data type file extension