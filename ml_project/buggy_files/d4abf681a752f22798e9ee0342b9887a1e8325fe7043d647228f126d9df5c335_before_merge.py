def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--asciidoc', help="Full path to python and "
                        "asciidoc.py. If not given, it's searched in PATH.",
                        nargs=2, required=False,
                        metavar=('PYTHON', 'ASCIIDOC'))
    parser.add_argument('--upload', help="Tag to upload the release for",
                        nargs=1, required=False, metavar='TAG')
    args = parser.parse_args()
    utils.change_cwd()

    upload_to_pypi = False

    if args.upload is not None:
        # Fail early when trying to upload without github3 installed
        # or without API token
        import github3  # pylint: disable=unused-variable
        read_github_token()

    run_asciidoc2html(args)
    if os.name == 'nt':
        if sys.maxsize > 2**32:
            # WORKAROUND
            print("Due to a python/Windows bug, this script needs to be run ")
            print("with a 32bit Python.")
            print()
            print("See http://bugs.python.org/issue24493 and ")
            print("https://github.com/pypa/virtualenv/issues/774")
            sys.exit(1)
        artifacts = build_windows()
    elif sys.platform == 'darwin':
        artifacts = build_mac()
    else:
        test_makefile()
        artifacts = build_sdist()
        upload_to_pypi = True

    if args.upload is not None:
        utils.print_title("Press enter to release...")
        input()
        github_upload(artifacts, args.upload[0])
        if upload_to_pypi:
            pypi_upload(artifacts)
    else:
        print()
        utils.print_title("Artifacts")
        for artifact in artifacts:
            print(artifact)