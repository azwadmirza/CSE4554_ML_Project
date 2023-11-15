    def update_alerts(self):
        if (
            self.project.access_control == self.project.ACCESS_PUBLIC
            and not self.license
            and not getattr(settings, "LOGIN_REQUIRED_URLS", None)
        ):
            self.add_alert("MissingLicense")
        else:
            self.delete_alert("MissingLicense")

        # Pick random translation with translated strings except source one
        translation = (
            self.translation_set.filter(unit__state__gte=STATE_TRANSLATED)
            .exclude(language=self.project.source_language)
            .first()
        )
        if translation:
            allunits = translation.unit_set
        else:
            allunits = self.source_translation.unit_set

        source_space = allunits.filter(source__contains=" ")
        target_space = allunits.filter(
            state__gte=STATE_TRANSLATED, target__contains=" "
        )
        if (
            not self.template
            and allunits.count() > 3
            and not source_space.exists()
            and target_space.exists()
        ):
            self.add_alert("MonolingualTranslation")
        else:
            self.delete_alert("MonolingualTranslation")
        if not self.can_push():
            self.delete_alert("PushFailure")

        if self.vcs not in VCS_REGISTRY or self.file_format not in FILE_FORMATS:
            self.add_alert(
                "UnsupportedConfiguration",
                vcs=self.vcs not in VCS_REGISTRY,
                file_format=self.file_format not in FILE_FORMATS,
            )
        else:
            self.delete_alert("UnsupportedConfiguration")

        base = self.linked_component if self.is_repo_link else self
        masks = [base.filemask]
        masks.extend(base.linked_childs.values_list("filemask", flat=True))
        duplicates = [item for item, count in Counter(masks).items() if count > 1]
        if duplicates:
            self.add_alert("DuplicateFilemask", duplicates=duplicates)
        else:
            self.delete_alert("DuplicateFilemask")

        location_error = None
        location_link = None
        if self.repoweb:
            unit = allunits.exclude(location="").first()
            if unit:
                for _location, filename, line in unit.get_locations():
                    location_link = self.get_repoweb_link(filename, line)
                    if location_link is None:
                        continue
                    # We only test first link
                    location_error = get_uri_error(location_link)
                    break
        if location_error:
            self.add_alert("BrokenBrowserURL", link=location_link, error=location_error)
        else:
            self.delete_alert("BrokenBrowserURL")
        if self.project.web:
            error = get_uri_error(self.project.web)
            if error is not None:
                self.add_alert("BrokenProjectURL", error=error)
            else:
                self.delete_alert("BrokenProjectURL")
        else:
            self.delete_alert("BrokenProjectURL")

        if self.screenshot_set.annotate(Count("units")).filter(units__count=0).exists():
            self.add_alert("UnusedScreenshot")
        else:
            self.delete_alert("UnusedScreenshot")