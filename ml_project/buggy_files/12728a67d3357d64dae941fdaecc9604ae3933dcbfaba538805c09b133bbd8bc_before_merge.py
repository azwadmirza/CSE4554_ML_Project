    def provide_context_and_uptodate(self, classification, lang, node=None):
        """Provide data for the context and the uptodate list for the list of the given classifiation."""
        hierarchy = self.extract_hierarchy(classification)
        kw = {
            "messages": self.site.MESSAGES,
        }
        page_kind = "list"
        if self.show_list_as_index:
            if not self.show_list_as_subcategories_list or len(hierarchy) == self.max_levels:
                page_kind = "index"
        if len(hierarchy) == 0:
            title = kw["messages"][lang]["Archive"]
            kw["is_feed_stale"] = False
        elif len(hierarchy) == 1:
            title = kw["messages"][lang]["Posts for year %s"] % hierarchy[0]
            kw["is_feed_stale"] = (datetime.datetime.utcnow().strftime("%Y") != hierarchy[0])
        elif len(hierarchy) == 2:
            title = kw["messages"][lang]["Posts for {month} {year}"].format(
                year=hierarchy[0],
                month=nikola.utils.LocaleBorg().get_month_name(int(hierarchy[1]), lang))
            kw["is_feed_stale"] = (datetime.datetime.utcnow().strftime("%Y/%m") != classification)
        elif len(hierarchy) == 3:
            title = kw["messages"][lang]["Posts for {month} {day}, {year}"].format(
                year=hierarchy[0],
                month=nikola.utils.LocaleBorg().get_month_name(int(hierarchy[1]), lang),
                day=int(hierarchy[2]))
            kw["is_feed_stale"] = (datetime.datetime.utcnow().strftime("%Y/%m/%d") != classification)
        else:
            raise Exception("Cannot interpret classification {}!".format(repr(classification)))

        context = {
            "title": title,
            "pagekind": [page_kind, "archive_page"],
            "create_archive_navigation": self.site.config["CREATE_ARCHIVE_NAVIGATION"],
            "archive_name": classification if classification else None
        }

        # Generate links for hierarchies
        if context["create_archive_navigation"]:
            if hierarchy:
                # Up level link makes sense only if this is not the top-level
                # page (hierarchy is empty)
                parent = '/'.join(hierarchy[:-1])
                context["up_archive"] = self.site.link('archive', parent, lang)
                context["up_archive_name"] = self.get_classification_friendly_name(parent, lang)
            else:
                context["up_archive"] = None
                context["up_archive_name"] = None

            nodelevel = len(hierarchy)
            flat_samelevel = self.archive_navigation[lang][nodelevel]
            idx = flat_samelevel.index(classification)
            if idx == -1:
                raise Exception("Cannot find classification {0} in flat hierarchy!".format(classification))
            previdx, nextidx = idx - 1, idx + 1
            # If the previous index is -1, or the next index is 1, the previous/next archive does not exist.
            context["previous_archive"] = self.site.link('archive', flat_samelevel[previdx], lang) if previdx != -1 else None
            context["previous_archive_name"] = self.get_classification_friendly_name(flat_samelevel[previdx], lang) if previdx != -1 else None
            context["next_archive"] = self.site.link('archive', flat_samelevel[nextidx], lang) if nextidx != len(flat_samelevel) else None
            context["next_archive_name"] = self.get_classification_friendly_name(flat_samelevel[nextidx], lang) if nextidx != len(flat_samelevel) else None
            context["archive_nodelevel"] = nodelevel
            context["has_archive_navigation"] = bool(context["previous_archive"] or context["up_archive"] or context["next_archive"])
        else:
            context["has_archive_navigation"] = False
        if page_kind == 'index':
            context["is_feed_stale"] = kw["is_feed_stale"]
        kw.update(context)
        return context, kw