    def sync_avatar_from_ldap(self, user: UserProfile, ldap_user: _LDAPUser) -> None:
        if 'avatar' in settings.AUTH_LDAP_USER_ATTR_MAP:
            # We do local imports here to avoid import loops
            from zerver.lib.upload import upload_avatar_image
            from zerver.lib.actions import do_change_avatar_fields
            from io import BytesIO

            avatar_attr_name = settings.AUTH_LDAP_USER_ATTR_MAP['avatar']
            if avatar_attr_name not in ldap_user.attrs:  # nocoverage
                # If this specific user doesn't have e.g. a
                # thumbnailPhoto set in LDAP, just skip that user.
                return

            io = BytesIO(ldap_user.attrs[avatar_attr_name][0])
            # Structurally, to make the S3 backend happy, we need to
            # provide a Content-Type; since that isn't specified in
            # any metadata, we auto-detect it.
            content_type = magic.from_buffer(copy.deepcopy(io).read()[0:1024], mime=True)
            if content_type.startswith("image/"):
                upload_avatar_image(io, user, user, content_type=content_type)
                do_change_avatar_fields(user, UserProfile.AVATAR_FROM_USER)
            else:
                logging.warning("Could not parse %s field for user %s" %
                                (avatar_attr_name, user.id))