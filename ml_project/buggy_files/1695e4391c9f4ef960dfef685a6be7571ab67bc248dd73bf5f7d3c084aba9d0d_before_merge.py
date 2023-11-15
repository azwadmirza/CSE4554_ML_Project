    def generic_post_list_renderer(self, lang, posts, output_name, template_name, filters, extra_context):
        """Render pages with lists of posts."""
        deps = []
        uptodate_deps = []
        for post in posts:
            deps += post.deps(lang)
            uptodate_deps += post.deps_uptodate(lang)

        context = {}
        context["posts"] = posts
        context["title"] = self.config['BLOG_TITLE'](lang)
        context["description"] = self.config['BLOG_DESCRIPTION'](lang)
        context["prevlink"] = None
        context["nextlink"] = None
        if extra_context:
            context.update(extra_context)

        post_deps_dict = {}
        post_deps_dict["posts"] = [(p.meta[lang]['title'], p.permalink(lang)) for p in posts]

        return self.generic_renderer(lang, output_name, template_name, filters,
                                     file_deps=deps,
                                     uptodate_deps=uptodate_deps,
                                     context=context,
                                     post_deps_dict=post_deps_dict)