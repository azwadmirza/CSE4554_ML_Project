def picard_reorder(picard, in_bam, ref_file, out_file):
    """Reorder BAM file to match reference file ordering.
    """
    if not file_exists(out_file):
        with tx_tmpdir(picard._config) as tmp_dir:
            with file_transaction(picard._config, out_file) as tx_out_file:
                dict_file = "%s.dict" % os.path.splitext(ref_file)[0]
                opts = [("INPUT", in_bam),
                        ("OUTPUT", tx_out_file),
                        ("SEQUENCE_DICTIONARY", dict_file),
                        ("ALLOW_INCOMPLETE_DICT_CONCORDANCE", "true"),
                        ("TMP_DIR", tmp_dir)]
                picard.run("ReorderSam", opts)
    return out_file