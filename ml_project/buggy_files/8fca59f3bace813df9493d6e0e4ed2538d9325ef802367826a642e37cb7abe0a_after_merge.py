def page_delete(request, pk):
    page = get_object_or_404(Page, pk=pk)
    if request.POST:
        menus = get_menus_that_need_update(page=page)
        page.delete()
        if menus:
            update_menus(menus)
        msg = pgettext_lazy("Dashboard message", "Removed page %s") % (page.title,)
        messages.success(request, msg)
        return redirect("dashboard:page-list")
    ctx = {"page": page}
    return TemplateResponse(request, "dashboard/page/modal_delete.html", ctx)