def generate_draft_news():
    root = Path(__file__).parents[1]
    exe = Path(sys.executable)
    towncrier = exe.with_name("towncrier{}".format(exe.suffix))
    new = subprocess.check_output([str(towncrier), "--draft", "--version", "NEXT"], cwd=root, universal_newlines=True)
    (root / "docs" / "_draft.rst").write_text("" if "No significant changes" in new else new)