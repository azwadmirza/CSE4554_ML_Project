def process_alignment(data, alt_input=None):
    """Do an alignment of fastq files, preparing a sorted BAM output file.
    """
    data = cwlutils.normalize_missing(utils.to_single_data(data))
    data = cwlutils.unpack_tarballs(data, data)
    fastq1, fastq2 = dd.get_input_sequence_files(data)
    if alt_input:
        fastq1, fastq2 = alt_input
    config = data["config"]
    aligner = config["algorithm"].get("aligner", None)
    if fastq1 and objectstore.file_exists_or_remote(fastq1) and aligner:
        logger.info("Aligning lane %s with %s aligner" % (data["rgnames"]["lane"], aligner))
        data = align_to_sort_bam(fastq1, fastq2, aligner, data)
        if dd.get_correct_umis(data):
            data["work_bam"] = postalign.correct_umis(data)
        if dd.get_umi_consensus(data):
            data["umi_bam"] = dd.get_work_bam(data)
            if fastq2:
                f1, f2, avg_cov = postalign.umi_consensus(data)
                data["config"]["algorithm"]["rawumi_avg_cov"] = avg_cov
                del data["config"]["algorithm"]["umi_type"]
                data["config"]["algorithm"]["mark_duplicates"] = False
                data = align_to_sort_bam(f1, f2, aligner, data)
            else:
                raise ValueError("Single fastq input for UMI processing; fgbio needs paired reads: %s" %
                                 dd.get_sample_name(data))
        data = _add_supplemental_bams(data)
    elif fastq1 and objectstore.file_exists_or_remote(fastq1) and fastq1.endswith(".bam"):
        sort_method = config["algorithm"].get("bam_sort")
        bamclean = config["algorithm"].get("bam_clean")
        if bamclean is True or bamclean == "picard":
            if sort_method and sort_method != "coordinate":
                raise ValueError("Cannot specify `bam_clean: picard` with `bam_sort` other than coordinate: %s"
                                 % sort_method)
            ref_file = dd.get_ref_file(data)
            out_bam = cleanbam.picard_prep(fastq1, data["rgnames"], ref_file, data["dirs"],
                                           data)
        elif bamclean == "fixrg":
            out_bam = cleanbam.fixrg(fastq1, data["rgnames"], dd.get_ref_file(data), data["dirs"], data)
        elif bamclean == "remove_extracontigs":
            out_bam = cleanbam.remove_extracontigs(fastq1, data)
        elif sort_method:
            runner = broad.runner_from_path("picard", config)
            out_file = os.path.join(data["dirs"]["work"], "{}-sort.bam".format(
                os.path.splitext(os.path.basename(fastq1))[0]))
            if not utils.file_exists(out_file):
                work_dir = utils.safe_makedir(os.path.join(dd.get_work_dir(data), "bamclean",
                                                           dd.get_sample_name(data)))
                out_file = os.path.join(work_dir, "{}-sort.bam".format(dd.get_sample_name(data)))
            out_bam = runner.run_fn("picard_sort", fastq1, sort_method, out_file)
        else:
            out_bam = _link_bam_file(fastq1, os.path.join(dd.get_work_dir(data), "prealign",
                                                          dd.get_sample_name(data)), data)
        bam.index(out_bam, data["config"])
        bam.check_header(out_bam, data["rgnames"], dd.get_ref_file(data), data["config"])
        dedup_bam = postalign.dedup_bam(out_bam, data)
        bam.index(dedup_bam, data["config"])
        data["work_bam"] = dedup_bam
    elif fastq1 and objectstore.file_exists_or_remote(fastq1) and fastq1.endswith(".cram"):
        data["work_bam"] = fastq1
    elif fastq1 is None and not dd.get_aligner(data):
        data["config"]["algorithm"]["variantcaller"] = False
        data["work_bam"] = None
    elif not fastq1:
        raise ValueError("No 'files' specified for input sample: %s" % dd.get_sample_name(data))
    elif "kraken" in config["algorithm"]:  # kraken doesn's need bam
        pass
    else:
        raise ValueError("Could not process input file from sample configuration. \n" +
                         fastq1 +
                         "\nIs the path to the file correct or is empty?\n" +
                         "If it is a fastq file (not pre-aligned BAM or CRAM), "
                         "is an aligner specified in the input configuration?")
    if data.get("work_bam"):
        # Add stable 'align_bam' target to use for retrieving raw alignment
        data["align_bam"] = data["work_bam"]
        data = _add_hla_files(data)
    return [[data]]