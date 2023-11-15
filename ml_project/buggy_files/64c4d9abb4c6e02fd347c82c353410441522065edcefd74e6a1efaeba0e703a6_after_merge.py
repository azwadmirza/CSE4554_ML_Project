def show(
    repo,
    all_branches=False,
    all_tags=False,
    revs=None,
    all_commits=False,
    sha_only=False,
):
    res = defaultdict(OrderedDict)

    if revs is None:
        revs = [repo.scm.get_rev()]

    revs = OrderedDict(
        (rev, None)
        for rev in repo.brancher(
            revs=revs,
            all_branches=all_branches,
            all_tags=all_tags,
            all_commits=all_commits,
            sha_only=True,
        )
    )

    for rev in revs:
        res[rev]["baseline"] = _collect_experiment(
            repo, rev, sha_only=sha_only
        )

    # collect reproduced experiments
    for exp_branch in repo.experiments.scm.list_branches():
        m = repo.experiments.BRANCH_RE.match(exp_branch)
        if m:
            rev = repo.scm.resolve_rev(m.group("baseline_rev"))
            if rev in revs:
                exp_rev = repo.experiments.scm.resolve_rev(exp_branch)
                with repo.experiments.chdir():
                    experiment = _collect_experiment(
                        repo.experiments.exp_dvc, exp_branch
                    )
                res[rev][exp_rev] = experiment

    # collect queued (not yet reproduced) experiments
    for stash_rev, entry in repo.experiments.stash_revs.items():
        if entry.baseline_rev in revs:
            with repo.experiments.chdir():
                experiment = _collect_experiment(
                    repo.experiments.exp_dvc, stash_rev, stash=True
                )
            res[entry.baseline_rev][stash_rev] = experiment

    return res