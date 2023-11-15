def list_quotas(request):
    from modoboa.lib.dbutils import db_type

    sort_order, sort_dir = get_sort_order(request.GET, "address")
    mboxes = Mailbox.objects.get_for_admin(
        request.user, request.GET.get("searchquery", None)
    )
    mboxes = mboxes.exclude(quota=0)
    if sort_order in ["address", "quota", "quota_value__bytes"]:
        mboxes = mboxes.order_by("%s%s" % (sort_dir, sort_order))
    elif sort_order == "quota_usage":
        where = "admin_mailbox.address||'@'||admin_domain.name"
        db_type = db_type()
        if db_type == "postgres":
            select = '(admin_quota.bytes::float / (CAST(admin_mailbox.quota AS BIGINT) * 1048576)) * 100'
        else:
            select = 'admin_quota.bytes / (admin_mailbox.quota * 1048576) * 100'
            if db_type == "mysql":
                where = "CONCAT(admin_mailbox.address,'@',admin_domain.name)"
        mboxes = mboxes.extra(
            select={'quota_usage': select},
            where=["admin_quota.username=%s" % where],
            tables=["admin_quota", "admin_domain"],
            order_by=["%s%s" % (sort_dir, sort_order)]
        )
    else:
        raise BadRequest(_("Invalid request"))
    page = get_listing_page(mboxes, request.GET.get("page", 1))
    context = {
        "headers": _render_to_string(
            request, "admin/quota_headers.html", {}
        )
    }
    if page is None:
        context["length"] = 0
    else:
        context["rows"] = _render_to_string(
            request, "admin/quotas.html", {
                "mboxes": page
            }
        )
        context["pages"] = [page.number]
    return render_to_json_response(context)