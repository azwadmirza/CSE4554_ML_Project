def move_tmp_log(logger):
    """ Move the temporary log file to the MultiQC data directory
    if it exists. """

    try:
        # https://stackoverflow.com/questions/15435652/python-does-not-release-filehandles-to-logfile
        logging.shutdown()
        shutil.copy(log_tmp_fn, os.path.join(config.data_dir, 'multiqc.log'))
        os.remove(log_tmp_fn)
        util_functions.robust_rmtree(log_tmp_dir)
    except (AttributeError, TypeError, IOError):
        pass