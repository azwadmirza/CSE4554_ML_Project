    def gen_tasks(self):
        """Render image galleries."""
        self.image_ext_list = self.image_ext_list_builtin
        self.image_ext_list.extend(self.site.config.get('EXTRA_IMAGE_EXTENSIONS', []))

        for k, v in self.site.GLOBAL_CONTEXT['template_hooks'].items():
            self.kw['||template_hooks|{0}||'.format(k)] = v._items

        self.site.scan_posts()
        yield self.group_task()

        template_name = "gallery.tmpl"

        # Create all output folders
        for task in self.create_galleries():
            yield task

        # For each gallery:
        for gallery, input_folder, output_folder in self.gallery_list:

            # Create subfolder list
            folder_list = [(x, x.split(os.sep)[-2]) for x in
                           glob.glob(os.path.join(gallery, '*') + os.sep)]

            # Parse index into a post (with translations)
            post = self.parse_index(gallery, input_folder, output_folder)

            # Create image list, filter exclusions
            image_list = self.get_image_list(gallery)

            # Create thumbnails and large images in destination
            for image in image_list:
                for task in self.create_target_images(image, input_folder):
                    yield task

            # Remove excluded images
            for image in self.get_excluded_images(gallery):
                for task in self.remove_excluded_image(image, input_folder):
                    yield task

            for lang in self.kw['translations']:
                # save navigation links as dependencies
                self.kw['navigation_links|{0}'.format(lang)] = self.kw['global_context']['navigation_links'](lang)

            # Create index.html for each language
            for lang in self.kw['translations']:

                dst = os.path.join(
                    self.kw['output_folder'],
                    self.site.path("gallery", gallery, lang))
                dst = os.path.normpath(dst)

                for k in self.site._GLOBAL_CONTEXT_TRANSLATABLE:
                    self.kw[k] = self.site.GLOBAL_CONTEXT[k](lang)

                context = {}
                context["lang"] = lang
                if post:
                    context["title"] = post.title(lang)
                else:
                    context["title"] = os.path.basename(gallery)
                context["description"] = None

                image_name_list = [os.path.basename(p) for p in image_list]

                if self.kw['use_filename_as_title']:
                    img_titles = []
                    for fn in image_name_list:
                        name_without_ext = os.path.splitext(os.path.basename(fn))[0]
                        img_titles.append(utils.unslugify(name_without_ext, lang))
                else:
                    img_titles = [''] * len(image_name_list)

                thumbs = ['.thumbnail'.join(os.path.splitext(p)) for p in image_list]
                thumbs = [os.path.join(self.kw['output_folder'], output_folder, os.path.relpath(t, input_folder)) for t in thumbs]
                dst_img_list = [os.path.join(output_folder, os.path.relpath(t, input_folder)) for t in image_list]
                dest_img_list = [os.path.join(self.kw['output_folder'], t) for t in dst_img_list]

                folders = []

                # Generate friendly gallery names
                for path, folder in folder_list:
                    fpost = self.parse_index(path, input_folder, output_folder)
                    if fpost:
                        ft = fpost.title(lang) or folder
                    else:
                        ft = folder
                    if not folder.endswith('/'):
                        folder += '/'
                    folders.append((folder, ft))

                context["folders"] = natsort.natsorted(
                    folders, alg=natsort.ns.F | natsort.ns.IC)
                context["crumbs"] = utils.get_crumbs(gallery, index_folder=self, lang=lang)
                context["permalink"] = self.site.link("gallery", gallery, lang)
                context["enable_comments"] = self.kw['comments_in_galleries']
                context["thumbnail_size"] = self.kw["thumbnail_size"]
                context["pagekind"] = ["gallery_front"]

                if post:
                    yield {
                        'basename': self.name,
                        'name': post.translated_base_path(lang),
                        'targets': [post.translated_base_path(lang)],
                        'file_dep': post.fragment_deps(lang),
                        'actions': [(post.compile, [lang])],
                        'uptodate': [utils.config_changed(self.kw.copy(), 'nikola.plugins.task.galleries:post')] + post.fragment_deps_uptodate(lang)
                    }
                    context['post'] = post
                else:
                    context['post'] = None
                file_dep = self.site.template_system.template_deps(
                    template_name) + image_list + thumbs
                file_dep_dest = self.site.template_system.template_deps(
                    template_name) + dest_img_list + thumbs
                if post:
                    file_dep += [post.translated_base_path(l) for l in self.kw['translations']]
                    file_dep_dest += [post.translated_base_path(l) for l in self.kw['translations']]

                context["pagekind"] = ["gallery_page"]

                yield utils.apply_filters({
                    'basename': self.name,
                    'name': dst,
                    'file_dep': file_dep,
                    'targets': [dst],
                    'actions': [
                        (self.render_gallery_index, (
                            template_name,
                            dst,
                            context.copy(),
                            dest_img_list,
                            img_titles,
                            thumbs,
                            file_dep))],
                    'clean': True,
                    'uptodate': [utils.config_changed({
                        1: self.kw.copy(),
                        2: self.site.config["COMMENTS_IN_GALLERIES"],
                        3: context.copy(),
                    }, 'nikola.plugins.task.galleries:gallery')],
                }, self.kw['filters'])

                # RSS for the gallery
                if self.kw["generate_rss"]:
                    rss_dst = os.path.join(
                        self.kw['output_folder'],
                        self.site.path("gallery_rss", gallery, lang))
                    rss_dst = os.path.normpath(rss_dst)

                    yield utils.apply_filters({
                        'basename': self.name,
                        'name': rss_dst,
                        'file_dep': file_dep_dest,
                        'targets': [rss_dst],
                        'actions': [
                            (self.gallery_rss, (
                                image_list,
                                dst_img_list,
                                img_titles,
                                lang,
                                self.site.link("gallery_rss", gallery, lang),
                                rss_dst,
                                context['title']
                            ))],
                        'clean': True,
                        'uptodate': [utils.config_changed({
                            1: self.kw.copy(),
                        }, 'nikola.plugins.task.galleries:rss')],
                    }, self.kw['filters'])