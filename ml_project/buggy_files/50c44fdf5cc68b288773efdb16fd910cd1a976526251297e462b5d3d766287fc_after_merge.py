def validate_plot_args(args: Dict[str, Any]) -> None:
    if not args.get('datadir') and not args.get('config'):
        raise OperationalException(
            "You need to specify either `--datadir` or `--config` "
            "for plot-profit and plot-dataframe.")