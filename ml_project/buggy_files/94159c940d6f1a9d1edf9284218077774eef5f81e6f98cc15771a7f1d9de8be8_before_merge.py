def generate_plot_filename(pair, timeframe) -> str:
    """
    Generate filenames per pair/timeframe to be used for storing plots
    """
    pair_name = pair.replace("/", "_")
    file_name = 'freqtrade-plot-' + pair_name + '-' + timeframe + '.html'

    logger.info('Generate plot file for %s', pair)

    return file_name