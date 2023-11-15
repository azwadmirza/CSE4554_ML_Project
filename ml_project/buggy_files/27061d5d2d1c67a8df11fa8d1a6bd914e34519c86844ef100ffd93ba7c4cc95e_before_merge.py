def upload_distribution():
    tools.assert_can_release()

    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "twine",
            "upload",
            "--skip-existing",
            "--config-file",
            tools.PYPIRC,
            os.path.join(DIST, "*"),
        ]
    )

    # Construct plain-text + markdown version of this changelog entry,
    # with link to canonical source.
    build_docs(builder="text")
    textfile = os.path.join(HYPOTHESIS_PYTHON, "docs", "_build", "text", "changes.txt")
    with open(textfile) as f:
        lines = f.readlines()
    entries = [i for i, l in enumerate(lines) if CHANGELOG_HEADER.match(l)]
    changelog_body = "".join(lines[entries[0] + 2 : entries[1]]).strip() + (
        "\n\n*[The canonical version of these notes (with links) is on readthedocs.]"
        "(https://hypothesis.readthedocs.io/en/latest/changes.html#v%s)*"
        % (current_version().replace(".", "-"),)
    )

    # Create a GitHub release, to trigger Zenodo DOI minting.  See
    # https://developer.github.com/v3/repos/releases/#create-a-release
    requests.post(
        "https://api.github.com/repos/HypothesisWorks/hypothesis/releases",
        json={
            "tag_name": tag_name(),
            "name": "Hypothesis for Python - version " + current_version(),
            "body": changelog_body,
        },
        timeout=120,  # seconds
        # Scoped personal access token, stored in Travis environ variable
        auth=("Zac-HD", os.environ["Zac_release_token"]),
    ).raise_for_status()

    # Post the release notes to Tidelift too - see https://tidelift.com/docs/api
    requests.post(
        "https://api.tidelift.com/external-api/lifting/pypi/hypothesis/release-notes/"
        + current_version(),
        json={"body": changelog_body},
        headers={"Authorization": "Bearer {}".format(os.environ["TIDELIFT_API_TOKEN"])},
        timeout=120,  # seconds
    ).raise_for_status()