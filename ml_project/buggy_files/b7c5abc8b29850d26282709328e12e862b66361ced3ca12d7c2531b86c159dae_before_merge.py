    def _execute(self, command, args):
        """Execute the deploy command."""
        self.logger = get_logger('deploy', STDERR_HANDLER)
        # Get last successful deploy date
        timestamp_path = os.path.join(self.site.config['CACHE_FOLDER'], 'lastdeploy')

        # Get last-deploy from persistent state
        last_deploy = self.site.state.get('last_deploy')
        if last_deploy is None:
            # If there is a last-deploy saved, move it to the new state persistence thing
            # FIXME: remove in Nikola 8
            if os.path.isfile(timestamp_path):
                try:
                    with io.open(timestamp_path, 'r', encoding='utf8') as inf:
                        last_deploy = dateutil.parser.parse(inf.read())
                        clean = False
                except (IOError, Exception) as e:
                    self.logger.debug("Problem when reading `{0}`: {1}".format(timestamp_path, e))
                    last_deploy = datetime(1970, 1, 1)
                    clean = True
                os.unlink(timestamp_path)  # Remove because from now on it's in state
            else:  # Just a default
                last_deploy = datetime(1970, 1, 1)
                clean = True
        else:
            last_deploy = dateutil.parser.parse(last_deploy)
            clean = False

        if self.site.config['COMMENT_SYSTEM_ID'] == 'nikolademo':
            self.logger.warn("\nWARNING WARNING WARNING WARNING\n"
                             "You are deploying using the nikolademo Disqus account.\n"
                             "That means you will not be able to moderate the comments in your own site.\n"
                             "And is probably not what you want to do.\n"
                             "Think about it for 5 seconds, I'll wait :-)\n\n")
            time.sleep(5)

        deploy_drafts = self.site.config.get('DEPLOY_DRAFTS', True)
        deploy_future = self.site.config.get('DEPLOY_FUTURE', False)
        undeployed_posts = []
        if not (deploy_drafts and deploy_future):
            # Remove drafts and future posts
            out_dir = self.site.config['OUTPUT_FOLDER']
            self.site.scan_posts()
            for post in self.site.timeline:
                if (not deploy_drafts and post.is_draft) or \
                   (not deploy_future and post.publish_later):
                    remove_file(os.path.join(out_dir, post.destination_path()))
                    remove_file(os.path.join(out_dir, post.source_path))
                    undeployed_posts.append(post)

        if args:
            presets = args
        else:
            presets = ['default']

        # test for preset existence
        for preset in presets:
            try:
                self.site.config['DEPLOY_COMMANDS'][preset]
            except:
                self.logger.error('No such preset: {0}'.format(preset))
                return 255

        for preset in presets:
            self.logger.info("=> preset '{0}'".format(preset))
            for command in self.site.config['DEPLOY_COMMANDS'][preset]:
                self.logger.info("==> {0}".format(command))
                try:
                    subprocess.check_call(command, shell=True)
                except subprocess.CalledProcessError as e:
                    self.logger.error('Failed deployment — command {0} '
                                      'returned {1}'.format(e.cmd, e.returncode))
                    return e.returncode

        self.logger.info("Successful deployment")

        new_deploy = datetime.utcnow()
        self._emit_deploy_event(last_deploy, new_deploy, clean, undeployed_posts)

        makedirs(self.site.config['CACHE_FOLDER'])
        # Store timestamp of successful deployment
        self.site.state.set('last_deploy', new_deploy.isoformat())