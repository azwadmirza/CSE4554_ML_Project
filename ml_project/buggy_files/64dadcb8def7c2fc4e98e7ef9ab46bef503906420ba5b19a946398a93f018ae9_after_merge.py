def messages_in_narrow_backend(request, user_profile,
                               msg_ids = REQ(validator=check_list(check_int)),
                               narrow = REQ(converter=narrow_parameter)):
    # type: (HttpRequest, UserProfile, List[int], Optional[List[Dict[str, Any]]]) -> HttpResponse

    # This query is limited to messages the user has access to because they
    # actually received them, as reflected in `zerver_usermessage`.
    query = select([column("message_id"), column("subject"), column("rendered_content")],
                   and_(column("user_profile_id") == literal(user_profile.id),
                        column("message_id").in_(msg_ids)),
                   join(table("zerver_usermessage"), table("zerver_message"),
                        literal_column("zerver_usermessage.message_id") ==
                        literal_column("zerver_message.id")))

    builder = NarrowBuilder(user_profile, column("message_id"))
    if narrow is not None:
        for term in narrow:
            query = builder.add_term(query, term)

    sa_conn = get_sqlalchemy_connection()
    query_result = list(sa_conn.execute(query).fetchall())

    search_fields = dict()
    for row in query_result:
        message_id = row['message_id']
        subject = row['subject']
        rendered_content = row['rendered_content']

        if 'content_matches' in row:
            content_matches = row['content_matches']
            subject_matches = row['subject_matches']
            search_fields[message_id] = get_search_fields(rendered_content, subject,
                                                          content_matches, subject_matches)
        else:
            search_fields[message_id] = dict(
                match_content=rendered_content,
                match_subject=subject
            )

    return json_success({"messages": search_fields})