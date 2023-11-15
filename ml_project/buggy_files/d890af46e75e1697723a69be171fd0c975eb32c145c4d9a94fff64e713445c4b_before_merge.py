    def interface(self):
        parser = argparse.ArgumentParser(
            description="""
            Multi-Region CloudFormation Test Deployment Tool)
            For more info see: http://taskcat.io
        """,
            prog='taskcat',
            prefix_chars='-',
            formatter_class=RawTextHelpFormatter)
        parser.add_argument(
            '-c',
            '--config_yml',
            type=str,
            help=" (Config File Required!) \n "
                 "example here: https://raw.githubusercontent.com/aws-quickstart/"
                 "taskcat/master/examples/sample-taskcat-project/ci/taskcat.yml"
        )
        parser.add_argument(
            '-P',
            '--boto_profile',
            type=str,
            help="Authenticate using boto profile")
        parser.add_argument(
            '-A',
            '--aws_access_key',
            type=str,
            help="AWS Access Key")
        parser.add_argument(
            '-S',
            '--aws_secret_key',
            type=str,
            help="AWS Secret Key")
        parser.add_argument(
            '-n',
            '--no_cleanup',
            action='store_true',
            help="Sets cleanup to false (Does not teardown stacks)")
        parser.add_argument(
            '-N',
            '--no_cleanup_failed',
            action='store_true',
            help="Sets cleaup to false if the stack launch fails (Does not teardown stacks if it experiences a failure)"
        )
        parser.add_argument(
            '-p',
            '--public_s3_bucket',
            action='store_true',
            help="Sets public_s3_bucket to True. (Accesses objects via public HTTP, not S3 API calls)")
        parser.add_argument(
            '-v',
            '--verbose',
            action='store_true',
            help="Enables verbosity")
        parser.add_argument(
            '-m',
            '--multithread_upload',
            action='store_true',
            help="Enables multithreaded upload to S3")
        parser.add_argument(
            '-t',
            '--tag',
            action=AppendTag,
            help="add tag to cloudformation stack, must be in the format TagKey=TagValue, multiple -t can be specified")
        parser.add_argument(
            '-s',
            '--stack-prefix',
            type=str,
            default="tag",
            help="set prefix for cloudformation stack name. only accepts lowercase letters, numbers and '-'")
        parser.add_argument(
            '-l',
            '--lint',
            type=str,
            default="warn",
            help="set linting 'strict' - will fail on errors and warnings, 'error' will fail on errors or 'warn' will "
                 "log errors to the console, but not fail")
        parser.add_argument(
            '-V',
            '--version',
            action='store_true',
            help="Prints Version")

        args = parser.parse_args()

        if len(sys.argv) == 1:
            self.welcome()
            print(parser.print_help())
            exit0()

        if args.version:
            print(get_installed_version())
            exit0()

        if not args.config_yml:
            parser.error("-c (--config_yml) not passed (Config File Required!)")
            print(parser.print_help())
            raise TaskCatException("-c (--config_yml) not passed (Config File Required!)")

        if args.multithread_upload:
            self.multithread_upload = True

        try:
            self.tags = args.tags
        except AttributeError:
            pass

        if not re.compile('^[a-z0-9\-]+$').match(args.stack_prefix):
            raise TaskCatException("--stack-prefix only accepts lowercase letters, numbers and '-'")
        self.stack_prefix = args.stack_prefix

        if args.verbose:
            self.verbose = True

        # Overrides Defaults for cleanup but does not overwrite config.yml
        if args.no_cleanup:
            self.run_cleanup = False

        if args.boto_profile is not None:
            if args.aws_access_key is not None or args.aws_secret_key is not None:
                parser.error("Cannot use boto profile -P (--boto_profile)" +
                             "with --aws_access_key or --aws_secret_key")
                print(parser.print_help())
                raise TaskCatException("Cannot use boto profile -P (--boto_profile)" +
                             "with --aws_access_key or --aws_secret_key")
        if args.public_s3_bucket:
            self.public_s3_bucket = True

        if args.no_cleanup_failed:
            if args.no_cleanup:
                parser.error("Cannot use -n (--no_cleanup) with -N (--no_cleanup_failed)")
                print(parser.print_help())
                raise TaskCatException("Cannot use -n (--no_cleanup) with -N (--no_cleanup_failed)")
            self.retain_if_failed = True

        return args