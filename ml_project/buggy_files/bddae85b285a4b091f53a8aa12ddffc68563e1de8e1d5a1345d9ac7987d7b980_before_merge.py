    def _execute(self, options, args):
        """Display site status."""
        self.site.scan_posts()

        timestamp_path = os.path.join(self.site.config["CACHE_FOLDER"], "lastdeploy")

        last_deploy = None

        try:
            with io.open(timestamp_path, "r", encoding="utf8") as inf:
                last_deploy = datetime.strptime(inf.read().strip(), "%Y-%m-%dT%H:%M:%S.%f")
                last_deploy_offset = datetime.utcnow() - last_deploy
        except (IOError, Exception):
            print("It does not seem like you’ve ever deployed the site (or cache missing).")

        if last_deploy:

            fmod_since_deployment = []
            for root, dirs, files in os.walk(self.site.config["OUTPUT_FOLDER"], followlinks=True):
                if not dirs and not files:
                    continue
                for fname in files:
                    fpath = os.path.join(root, fname)
                    fmodtime = datetime.fromtimestamp(os.stat(fpath).st_mtime)
                    if fmodtime.replace(tzinfo=tzlocal()) > last_deploy.replace(tzinfo=gettz("UTC")).astimezone(tz=tzlocal()):
                        fmod_since_deployment.append(fpath)

            if len(fmod_since_deployment) > 0:
                print("{0} output files modified since last deployment {1} ago.".format(str(len(fmod_since_deployment)), self.human_time(last_deploy_offset)))
                if options['list_modified']:
                    for fpath in fmod_since_deployment:
                        print("Modified: '{0}'".format(fpath))
            else:
                print("Last deployment {0} ago.".format(self.human_time(last_deploy_offset)))

        now = datetime.utcnow().replace(tzinfo=gettz("UTC"))

        posts_count = len(self.site.all_posts)

        # find all drafts
        posts_drafts = [post for post in self.site.all_posts if post.is_draft]
        posts_drafts = sorted(posts_drafts, key=lambda post: post.source_path)

        # find all scheduled posts with offset from now until publishing time
        posts_scheduled = [(post.date - now, post) for post in self.site.all_posts if post.publish_later]
        posts_scheduled = sorted(posts_scheduled, key=lambda offset_post: (offset_post[0], offset_post[1].source_path))

        if len(posts_scheduled) > 0:
            if options['list_scheduled']:
                for offset, post in posts_scheduled:
                    print("Scheduled: '{1}' ({2}; source: {3}) in {0}".format(self.human_time(offset), post.meta('title'), post.permalink(), post.source_path))
            else:
                offset, post = posts_scheduled[0]
                print("{0} to next scheduled post ('{1}'; {2}; source: {3}).".format(self.human_time(offset), post.meta('title'), post.permalink(), post.source_path))
        if options['list_drafts']:
            for post in posts_drafts:
                print("Draft: '{0}' ({1}; source: {2})".format(post.meta('title'), post.permalink(), post.source_path))
        print("{0} posts in total, {1} scheduled, and {2} drafts.".format(posts_count, len(posts_scheduled), len(posts_drafts)))