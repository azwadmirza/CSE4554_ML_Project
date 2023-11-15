def show_metrics(
    metrics, all_branches=False, all_tags=False, all_commits=False
):
    from dvc.utils.diff import format_dict
    from dvc.utils.flatten import flatten

    # When `metrics` contains a `None` key, it means that some files
    # specified as `targets` in `repo.metrics.show` didn't contain any metrics.
    missing = metrics.pop(None, None)

    for branch, val in metrics.items():
        if all_branches or all_tags or all_commits:
            logger.info(f"{branch}:")

        for fname, metric in val.items():
            if not isinstance(metric, dict):
                logger.info("\t{}: {}".format(fname, str(metric)))
                continue

            logger.info(f"\t{fname}:")
            for key, value in flatten(format_dict(metric)).items():
                logger.info(f"\t\t{key}: {value}")

    if missing:
        raise BadMetricError(missing)