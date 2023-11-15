def benchmark(ref_samples: list, samples: list):
    """
    Performace benchmark of samples.

    Please see :meth:`pythainlp.benchmarks.word_tokenization.compute_stats` for
    metrics being computed.

    :param list[str] ref_samples: ground truth samples
    :param list[str] samples: samples that we want to evaluate

    :return: dataframe with row x col = len(samples) x len(metrics)
    :rtype: pandas.DataFrame
    """
    results = []
    for i, (r, s) in enumerate(zip(ref_samples, samples)):
        try:
            r, s = preprocessing(r), preprocessing(s)
            if r and s:
                stats = compute_stats(r, s)
                stats = _flatten_result(stats)
                stats["expected"] = r
                stats["actual"] = s
                results.append(stats)
        except:
            reason = """
[Error]
Reason: %s

Pair (i=%d)
--- label
%s
--- sample
%s
""" % (
                sys.exc_info(),
                i,
                r,
                s,
            )
            raise SystemExit(reason)

    return pd.DataFrame(results)