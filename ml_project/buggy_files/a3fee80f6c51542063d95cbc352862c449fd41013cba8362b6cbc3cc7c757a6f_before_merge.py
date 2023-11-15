def orchestrate(
    mods, saltenv="base", test=None, exclude=None, pillar=None, pillarenv=None
):
    """
    .. versionadded:: 2016.11.0

    Execute the orchestrate runner from a masterless minion.

    .. seealso:: More Orchestrate documentation

        * :ref:`Full Orchestrate Tutorial <orchestrate-runner>`
        * :py:mod:`Docs for the ``salt`` state module <salt.states.saltmod>`

    CLI Examples:

    .. code-block:: bash

        salt-call --local state.orchestrate webserver
        salt-call --local state.orchestrate webserver saltenv=dev test=True
        salt-call --local state.orchestrate webserver saltenv=dev pillarenv=aws
    """
    return _orchestrate(
        mods=mods,
        saltenv=saltenv,
        test=test,
        exclude=exclude,
        pillar=pillar,
        pillarenv=pillarenv,
    )