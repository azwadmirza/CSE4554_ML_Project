    def __init__(
        self,
        link,          # type: Link
        template,        # type: InstallRequirement
        factory,       # type: Factory
        name=None,     # type: Optional[str]
        version=None,  # type: Optional[_BaseVersion]
    ):
        # type: (...) -> None
        source_link = link
        cache_entry = factory.get_wheel_cache_entry(link, name)
        if cache_entry is not None:
            logger.debug("Using cached wheel link: %s", cache_entry.link)
            link = cache_entry.link
        ireq = make_install_req_from_link(link, template)
        assert ireq.link == link
        if ireq.link.is_wheel and not ireq.link.is_file:
            wheel = Wheel(ireq.link.filename)
            wheel_name = canonicalize_name(wheel.name)
            assert name == wheel_name, (
                "{!r} != {!r} for wheel".format(name, wheel_name)
            )
            # Version may not be present for PEP 508 direct URLs
            if version is not None:
                wheel_version = Version(wheel.version)
                assert version == wheel_version, (
                    "{!r} != {!r} for wheel {}".format(
                        version, wheel_version, name
                    )
                )

        if (cache_entry is not None and
                cache_entry.persistent and
                template.link is template.original_link):
            ireq.original_link_is_in_wheel_cache = True

        super(LinkCandidate, self).__init__(
            link=link,
            source_link=source_link,
            ireq=ireq,
            factory=factory,
            name=name,
            version=version,
        )