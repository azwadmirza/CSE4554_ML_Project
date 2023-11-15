def generate_draft_news():
    root = Path(__file__).parents[1]
    new = subprocess.check_output(
        [sys.executable, "-m", "towncrier", "--draft", "--version", "NEXT"], cwd=root, universal_newlines=True,
    )
    (root / "docs" / "_draft.rst").write_text("" if "No significant changes" in new else new)