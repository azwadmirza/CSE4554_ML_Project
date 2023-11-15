    def _extract_comment(self, comment, wordpress_namespace):
        """Extract comment from dump."""
        id = int(get_text_tag(comment, "{{{0}}}comment_id".format(wordpress_namespace), None))
        author = get_text_tag(comment, "{{{0}}}comment_author".format(wordpress_namespace), None)
        author_email = get_text_tag(comment, "{{{0}}}comment_author_email".format(wordpress_namespace), None)
        author_url = get_text_tag(comment, "{{{0}}}comment_author_url".format(wordpress_namespace), None)
        author_IP = get_text_tag(comment, "{{{0}}}comment_author_IP".format(wordpress_namespace), None)
        # date = get_text_tag(comment, "{{{0}}}comment_date".format(wordpress_namespace), None)
        date_gmt = get_text_tag(comment, "{{{0}}}comment_date_gmt".format(wordpress_namespace), None)
        content = get_text_tag(comment, "{{{0}}}comment_content".format(wordpress_namespace), None)
        approved = get_text_tag(comment, "{{{0}}}comment_approved".format(wordpress_namespace), '0')
        if approved == '0':
            approved = 'hold'
        elif approved == '1':
            approved = 'approved'
        elif approved == 'spam' or approved == 'trash':
            pass
        else:
            LOGGER.warn("Unknown comment approved status: {0}".format(approved))
        parent = int(get_text_tag(comment, "{{{0}}}comment_parent".format(wordpress_namespace), 0))
        if parent == 0:
            parent = None
        user_id = int(get_text_tag(comment, "{{{0}}}comment_user_id".format(wordpress_namespace), 0))
        if user_id == 0:
            user_id = None

        if approved == 'trash' or approved == 'spam':
            return None

        return {"id": id, "status": str(approved), "approved": approved == "approved",
                "author": author, "email": author_email, "url": author_url, "ip": author_IP,
                "date": date_gmt, "content": content, "parent": parent, "user_id": user_id}