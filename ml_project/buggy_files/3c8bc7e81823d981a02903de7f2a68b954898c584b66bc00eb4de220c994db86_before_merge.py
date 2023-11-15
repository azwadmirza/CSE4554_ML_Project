def process_message_files(message: ZerverFieldsT,
                          domain_name: str,
                          realm_id: int,
                          message_id: int,
                          user: str,
                          users: List[ZerverFieldsT],
                          added_users: AddedUsersT,
                          zerver_attachment: List[ZerverFieldsT],
                          uploads_list: List[ZerverFieldsT]) -> Dict[str, Any]:
    has_attachment = False
    has_image = False
    has_link = False

    files = message.get('files', [])

    subtype = message.get('subtype')

    if subtype == 'file_share':
        # In Slack messages, uploads can either have the subtype as 'file_share' or
        # have the upload information in 'files' keyword
        files = [message['file']]

    markdown_links = []

    for fileinfo in files:
        url = fileinfo['url_private']

        if 'files.slack.com' in url:
            # For attachments with slack download link
            has_attachment = True
            has_link = True
            has_image = True if 'image' in fileinfo['mimetype'] else False

            file_user = [iterate_user for iterate_user in users if message['user'] == iterate_user['id']]
            file_user_email = get_user_email(file_user[0], domain_name)

            s3_path, content_for_link = get_attachment_path_and_content(fileinfo, realm_id)
            markdown_links.append(content_for_link)

            # construct attachments
            build_uploads(added_users[user], realm_id, file_user_email, fileinfo, s3_path,
                          uploads_list)

            build_attachment(realm_id, {message_id}, added_users[user],
                             fileinfo, s3_path, zerver_attachment)
        else:
            # For attachments with link not from slack
            # Example: Google drive integration
            has_link = True
            if 'title' in fileinfo:
                file_name = fileinfo['title']
            else:
                file_name = fileinfo['name']
            markdown_links.append('[%s](%s)' % (file_name, fileinfo['url_private']))

    content = '\n'.join(markdown_links)

    return dict(
        content=content,
        has_attachment=has_attachment,
        has_image=has_image,
        has_link=has_link,
    )