def _mapclassify_choro(values, scheme, **classification_kwds):
    """
    Wrapper for choropleth schemes from mapclassify for use with plot_dataframe

    Parameters
    ----------
    values
        Series to be plotted
    scheme : str
        One of mapclassify classification schemes
        Options are BoxPlot, EqualInterval, FisherJenks,
        FisherJenksSampled, HeadTailBreaks, JenksCaspall,
        JenksCaspallForced, JenksCaspallSampled, MaxP,
        MaximumBreaks, NaturalBreaks, Quantiles, Percentiles, StdMean,
        UserDefined

    **classification_kwds : dict
        Keyword arguments for classification scheme
        For details see mapclassify documentation:
        https://mapclassify.readthedocs.io/en/latest/api.html

    Returns
    -------
    binning
        Binning objects that holds the Series with values replaced with
        class identifier and the bins.
    """
    try:
        import mapclassify.classifiers as classifiers

    except ImportError:
        raise ImportError(
            "The 'mapclassify' >= 2.2.0 package is required to use the 'scheme' keyword"
        )
    from mapclassify import __version__ as mc_version

    if mc_version < LooseVersion("2.2.0"):
        raise ImportError(
            "The 'mapclassify' >= 2.2.0 package is required to "
            "use the 'scheme' keyword"
        )
    schemes = {}
    for classifier in classifiers.CLASSIFIERS:
        schemes[classifier.lower()] = getattr(classifiers, classifier)

    scheme = scheme.lower()

    # mapclassify < 2.1 cleaned up the scheme names (removing underscores)
    # trying both to keep compatibility with older versions and provide
    # compatibility with newer versions of mapclassify
    oldnew = {
        "Box_Plot": "BoxPlot",
        "Equal_Interval": "EqualInterval",
        "Fisher_Jenks": "FisherJenks",
        "Fisher_Jenks_Sampled": "FisherJenksSampled",
        "HeadTail_Breaks": "HeadTailBreaks",
        "Jenks_Caspall": "JenksCaspall",
        "Jenks_Caspall_Forced": "JenksCaspallForced",
        "Jenks_Caspall_Sampled": "JenksCaspallSampled",
        "Max_P_Plassifier": "MaxP",
        "Maximum_Breaks": "MaximumBreaks",
        "Natural_Breaks": "NaturalBreaks",
        "Std_Mean": "StdMean",
        "User_Defined": "UserDefined",
    }
    scheme_names_mapping = {}
    scheme_names_mapping.update(
        {old.lower(): new.lower() for old, new in oldnew.items()}
    )
    scheme_names_mapping.update(
        {new.lower(): old.lower() for old, new in oldnew.items()}
    )

    try:
        scheme_class = schemes[scheme]
    except KeyError:
        scheme = scheme_names_mapping.get(scheme, scheme)
        try:
            scheme_class = schemes[scheme]
        except KeyError:
            raise ValueError(
                "Invalid scheme. Scheme must be in the set: %r" % schemes.keys()
            )

    if classification_kwds["k"] is not None:
        from inspect import getfullargspec as getspec

        spec = getspec(scheme_class.__init__)
        if "k" not in spec.args:
            del classification_kwds["k"]
    try:
        binning = scheme_class(values, **classification_kwds)
    except TypeError:
        raise TypeError("Invalid keyword argument for %r " % scheme)
    return binning