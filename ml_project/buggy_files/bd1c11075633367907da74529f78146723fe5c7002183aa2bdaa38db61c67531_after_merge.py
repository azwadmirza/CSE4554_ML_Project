    def gen_tasks(self):
        self.site.scan_posts()
        yield self.group_task()

        kw = {
            "translations": self.site.config['TRANSLATIONS'],
            "index_display_post_count":
            self.site.config['INDEX_DISPLAY_POST_COUNT'],
            "messages": self.site.MESSAGES,
            "index_teasers": self.site.config['INDEX_TEASERS'],
            "output_folder": self.site.config['OUTPUT_FOLDER'],
            "filters": self.site.config['FILTERS'],
            "show_untranslated_posts": self.site.config['SHOW_UNTRANSLATED_POSTS'],
            "indexes_title": self.site.config['INDEXES_TITLE'],
            "indexes_pages": self.site.config['INDEXES_PAGES'],
            "indexes_pages_main": self.site.config['INDEXES_PAGES_MAIN'],
            "blog_title": self.site.config["BLOG_TITLE"],
            "rss_read_more_link": self.site.config["RSS_READ_MORE_LINK"],
        }

        template_name = "index.tmpl"
        posts = self.site.posts
        for lang in kw["translations"]:
            # Split in smaller lists
            lists = []
            if kw["show_untranslated_posts"]:
                filtered_posts = posts
            else:
                filtered_posts = [x for x in posts if x.is_translation_available(lang)]
            lists.append(filtered_posts[:kw["index_display_post_count"]])
            filtered_posts = filtered_posts[kw["index_display_post_count"]:]
            while filtered_posts:
                lists.append(filtered_posts[-kw["index_display_post_count"]:])
                filtered_posts = filtered_posts[:-kw["index_display_post_count"]]
            num_pages = len(lists)
            for i, post_list in enumerate(lists):
                context = {}
                indexes_title = kw['indexes_title'] or kw['blog_title'](lang)
                if kw["indexes_pages_main"]:
                    ipages_i = i + 1
                    ipages_msg = "page %d"
                else:
                    ipages_i = i
                    ipages_msg = "old posts, page %d"
                if kw["indexes_pages"]:
                    indexes_pages = kw["indexes_pages"] % ipages_i
                else:
                    indexes_pages = " (" + \
                        kw["messages"][lang][ipages_msg] % ipages_i + ")"
                if i > 0 or kw["indexes_pages_main"]:
                    context["title"] = indexes_title + indexes_pages
                else:
                    context["title"] = indexes_title
                context["prevlink"] = None
                context["nextlink"] = None
                context['index_teasers'] = kw['index_teasers']
                if i == 0:  # index.html page
                    context["prevlink"] = None
                    if num_pages > 1:
                        context["nextlink"] = "index-{0}.html".format(num_pages - 1)
                    else:
                        context["nextlink"] = None
                else:  # index-x.html pages
                    if i > 1:
                        context["nextlink"] = "index-{0}.html".format(i - 1)
                    if i < num_pages - 1:
                        context["prevlink"] = "index-{0}.html".format(i + 1)
                    elif i == num_pages - 1:
                        context["prevlink"] = "index.html"
                context["permalink"] = self.site.link("index", i, lang)
                output_name = os.path.join(
                    kw['output_folder'], self.site.path("index", i,
                                                        lang))
                task = self.site.generic_post_list_renderer(
                    lang,
                    post_list,
                    output_name,
                    template_name,
                    kw['filters'],
                    context,
                )
                task_cfg = {1: task['uptodate'][0].config, 2: kw}
                task['uptodate'] = [config_changed(task_cfg)]
                task['basename'] = 'render_indexes'
                yield task

        if not self.site.config["STORY_INDEX"]:
            return
        kw = {
            "translations": self.site.config['TRANSLATIONS'],
            "post_pages": self.site.config["post_pages"],
            "output_folder": self.site.config['OUTPUT_FOLDER'],
            "filters": self.site.config['FILTERS'],
            "index_file": self.site.config['INDEX_FILE'],
        }
        template_name = "list.tmpl"
        for lang in kw["translations"]:
            # Need to group by folder to avoid duplicated tasks (Issue #758)
                # Group all pages by path prefix
                groups = defaultdict(list)
                for p in self.site.timeline:
                    if not p.is_post:
                        dirname = os.path.dirname(p.destination_path(lang))
                        groups[dirname].append(p)
                for dirname, post_list in groups.items():
                    context = {}
                    context["items"] = []
                    should_render = True
                    output_name = os.path.join(kw['output_folder'], dirname, kw['index_file'])
                    short_destination = os.path.join(dirname, kw['index_file'])
                    context["permalink"] = '/' + short_destination.replace('\\', '/')

                    for post in post_list:
                        # If there is an index.html pending to be created from
                        # a story, do not generate the STORY_INDEX
                        if post.destination_path(lang) == short_destination:
                            should_render = False
                        else:
                            context["items"].append((post.title(lang),
                                                     post.permalink(lang)))

                    if should_render:
                        task = self.site.generic_post_list_renderer(lang, post_list,
                                                                    output_name,
                                                                    template_name,
                                                                    kw['filters'],
                                                                    context)
                        task_cfg = {1: task['uptodate'][0].config, 2: kw}
                        task['uptodate'] = [config_changed(task_cfg)]
                        task['basename'] = self.name
                        yield task