    def generic_index_renderer(self, lang, posts, indexes_title, template_name, context_source, kw, basename, page_link, page_path, additional_dependencies=[]):
        """Create an index page.

        lang: The language
        posts: A list of posts
        indexes_title: Title
        template_name: Name of template file
        context_source: This will be copied and extended and used as every
                        page's context
        kw: An extended version will be used for uptodate dependencies
        basename: Basename for task
        page_link: A function accepting an index i, the displayed page number,
                   the number of pages, and a boolean force_addition
                   which creates a link to the i-th page (where i ranges
                   between 0 and num_pages-1). The displayed page (between 1
                   and num_pages) is the number (optionally) displayed as
                   'page %d' on the rendered page. If force_addition is True,
                   the appendum (inserting '-%d' etc.) should be done also for
                   i == 0.
        page_path: A function accepting an index i, the displayed page number,
                   the number of pages, and a boolean force_addition,
                   which creates a path to the i-th page. All arguments are
                   as the ones for page_link.
        additional_dependencies: a list of dependencies which will be added
                                 to task['uptodate']
        """
        # Update kw
        kw = kw.copy()
        kw["tag_pages_are_indexes"] = self.config['TAG_PAGES_ARE_INDEXES']
        kw["index_display_post_count"] = self.config['INDEX_DISPLAY_POST_COUNT']
        kw["index_teasers"] = self.config['INDEX_TEASERS']
        kw["indexes_pages"] = self.config['INDEXES_PAGES'](lang)
        kw["indexes_pages_main"] = self.config['INDEXES_PAGES_MAIN']
        kw["indexes_static"] = self.config['INDEXES_STATIC']
        kw['indexes_pretty_page_url'] = self.config["INDEXES_PRETTY_PAGE_URL"]
        kw['demote_headers'] = self.config['DEMOTE_HEADERS']
        kw['generate_atom'] = self.config["GENERATE_ATOM"]
        kw['feed_links_append_query'] = self.config["FEED_LINKS_APPEND_QUERY"]
        kw['currentfeed'] = None
        kw['show_index_page_navigation'] = self.config['SHOW_INDEX_PAGE_NAVIGATION']

        # Split in smaller lists
        lists = []
        if kw["indexes_static"]:
            lists.append(posts[:kw["index_display_post_count"]])
            posts = posts[kw["index_display_post_count"]:]
            while posts:
                lists.append(posts[-kw["index_display_post_count"]:])
                posts = posts[:-kw["index_display_post_count"]]
        else:
            while posts:
                lists.append(posts[:kw["index_display_post_count"]])
                posts = posts[kw["index_display_post_count"]:]
            if not lists:
                lists.append([])
        num_pages = len(lists)
        displayed_page_numbers = [utils.get_displayed_page_number(i, num_pages, self) for i in range(num_pages)]
        page_links = [page_link(i, page_number, num_pages, False) for i, page_number in enumerate(displayed_page_numbers)]
        if kw['show_index_page_navigation']:
            # Since the list displayed_page_numbers is not necessarily
            # sorted -- in case INDEXES_STATIC is True, it is of the
            # form [num_pages, 1, 2, ..., num_pages - 1] -- we order it
            # via a map. This allows to not replicate the logic of
            # utils.get_displayed_page_number() here.
            if not kw["indexes_pages_main"] and not kw["indexes_static"]:
                temp_map = {page_number: link for page_number, link in zip(displayed_page_numbers, page_links)}
            else:
                temp_map = {page_number - 1: link for page_number, link in zip(displayed_page_numbers, page_links)}
            page_links_context = [temp_map[i] for i in range(num_pages)]
        for i, post_list in enumerate(lists):
            context = context_source.copy()
            if 'pagekind' not in context:
                context['pagekind'] = ['index']
            ipages_i = displayed_page_numbers[i]
            if kw["indexes_pages"]:
                indexes_pages = kw["indexes_pages"] % ipages_i
            else:
                if kw["indexes_pages_main"]:
                    ipages_msg = "page %d"
                else:
                    ipages_msg = "old posts, page %d"
                indexes_pages = " (" + \
                    kw["messages"][lang][ipages_msg] % ipages_i + ")"
            if i > 0 or kw["indexes_pages_main"]:
                context["title"] = indexes_title + indexes_pages
            else:
                context["title"] = indexes_title
            context["prevlink"] = None
            context["nextlink"] = None
            context['index_teasers'] = kw['index_teasers']
            prevlink = None
            nextlink = None
            if kw["indexes_static"]:
                if i > 0:
                    if i < num_pages - 1:
                        prevlink = i + 1
                    elif i == num_pages - 1:
                        prevlink = 0
                if num_pages > 1:
                    if i > 1:
                        nextlink = i - 1
                    elif i == 0:
                        nextlink = num_pages - 1
            else:
                if i >= 1:
                    prevlink = i - 1
                if i < num_pages - 1:
                    nextlink = i + 1
            if prevlink is not None:
                context["prevlink"] = page_links[prevlink]
                context["prevfeedlink"] = page_link(prevlink, displayed_page_numbers[prevlink],
                                                    num_pages, False, extension=".atom")
            if nextlink is not None:
                context["nextlink"] = page_links[nextlink]
                context["nextfeedlink"] = page_link(nextlink, displayed_page_numbers[nextlink],
                                                    num_pages, False, extension=".atom")
            context['show_index_page_navigation'] = kw['show_index_page_navigation']
            if kw['show_index_page_navigation']:
                context['page_links'] = page_links_context
                if not kw["indexes_pages_main"] and not kw["indexes_static"]:
                    context['current_page'] = ipages_i
                else:
                    context['current_page'] = ipages_i - 1
                context['prev_next_links_reversed'] = kw['indexes_static']
            context["permalink"] = page_links[i]
            output_name = os.path.join(kw['output_folder'], page_path(i, ipages_i, num_pages, False))
            task = self.generic_post_list_renderer(
                lang,
                post_list,
                output_name,
                template_name,
                kw['filters'],
                context,
            )
            task['uptodate'] = task['uptodate'] + [utils.config_changed(kw, 'nikola.nikola.Nikola.generic_index_renderer')] + additional_dependencies
            task['basename'] = basename
            yield task

            if kw['generate_atom']:
                atom_output_name = os.path.join(kw['output_folder'], page_path(i, ipages_i, num_pages, False, extension=".atom"))
                context["feedlink"] = page_link(i, ipages_i, num_pages, False, extension=".atom")
                if not kw["currentfeed"]:
                    kw["currentfeed"] = context["feedlink"]
                context["currentfeedlink"] = kw["currentfeed"]
                context["feedpagenum"] = i
                context["feedpagecount"] = num_pages
                kw['feed_teasers'] = self.config['FEED_TEASERS']
                kw['feed_plain'] = self.config['FEED_PLAIN']
                kw['feed_previewimage'] = self.config['FEED_PREVIEWIMAGE']
                atom_task = {
                    "basename": basename,
                    "name": atom_output_name,
                    "file_dep": sorted([_.base_path for _ in post_list]),
                    "task_dep": ['render_posts'],
                    "targets": [atom_output_name],
                    "actions": [(self.atom_feed_renderer,
                                (lang,
                                 post_list,
                                 atom_output_name,
                                 kw['filters'],
                                 context,))],
                    "clean": True,
                    "uptodate": [utils.config_changed(kw, 'nikola.nikola.Nikola.atom_feed_renderer')] + additional_dependencies
                }
                yield utils.apply_filters(atom_task, kw['filters'])

        if kw["indexes_pages_main"] and kw['indexes_pretty_page_url'](lang):
            # create redirection
            output_name = os.path.join(kw['output_folder'], page_path(0, displayed_page_numbers[0], num_pages, True))
            link = page_links[0]
            yield utils.apply_filters({
                'basename': basename,
                'name': output_name,
                'targets': [output_name],
                'actions': [(utils.create_redirect, (output_name, link))],
                'clean': True,
                'uptodate': [utils.config_changed(kw, 'nikola.nikola.Nikola.generic_index_renderer')],
            }, kw["filters"])