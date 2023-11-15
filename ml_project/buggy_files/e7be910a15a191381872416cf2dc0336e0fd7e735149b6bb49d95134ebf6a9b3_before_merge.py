def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        prog='Tern',
        description='''
    Tern is a container image component curation tool. Tern retrieves
    information about packages that are installed in a container image.
    Learn more at https://github.com/vmware/tern''')
    parser.add_argument('-l', '--log-stream', action='store_true',
                        help="Stream logs to the console; "
                        "Useful when running in a shell")
    parser.add_argument('-c', '--clear-cache', action='store_true',
                        help="Clear the cache before running")
    parser.add_argument('-k', '--keep-wd', action='store_true',
                        help="Keep the working directory after execution."
                        " Useful when debugging container images")
    parser.add_argument('-b', '--bind-mount', action='store_true',
                        help="Treat working directory as a bind mount."
                        " Needed when running from within a container")
    parser.add_argument('-r', '--redo', action='store_true',
                        help="Repopulate the cache for found layers")
    # sys.version gives more information than we care to print
    py_ver = sys.version.replace('\n', '').split('[')[0]
    parser.add_argument('-v', '--version', action='version',
                        version="{ver_str}\n   python version = {py_v}".format(
                            ver_str=get_version(), py_v=py_ver))
    subparsers = parser.add_subparsers(help='Subcommands')
    # subparser for report
    parser_report = subparsers.add_parser('report',
                                          help="Create a BoM report."
                                          " Run 'tern report -h' for"
                                          " report format options.")
    parser_report.add_argument('-d', '--dockerfile', type=check_file_existence,
                               help="Dockerfile used to build the Docker"
                               " image")
    parser_report.add_argument('-i', '--docker-image',
                               help="Docker image that exists locally -"
                               " image:tag"
                               " The option can be used to pull docker"
                               " images by digest as well -"
                               " <repo>@<digest-type>:<digest>")
    parser_report.add_argument('-w', '--raw-image', metavar='FILE',
                               help="Raw container image that exists locally "
                               "in the form of a tar archive.")
    parser_report.add_argument('-x', '--extend', metavar='EXTENSION',
                               help="Use an extension to analyze a container "
                               "image. Available extensions: cve-bin-tool")
    parser_report.add_argument('-f', '--report-format',
                               metavar='REPORT_FORMAT',
                               help="Format the report using one of the "
                               "available formats: "
                               "spdxtagvalue, json, yaml")
    parser_report.add_argument('-o', '--output-file', default=None,
                               metavar='FILE',
                               help="Write the report to a file. "
                               "If no file is given the default file in "
                               "utils/constants.py will be used")
    parser_report.set_defaults(name='report')
    args = parser.parse_args()

    # execute
    if sys.version_info < (3, 0):
        sys.stderr.write("Error running Tern. Please check that python3 "
                         "is configured as default.\n")
    else:
        do_main(args)