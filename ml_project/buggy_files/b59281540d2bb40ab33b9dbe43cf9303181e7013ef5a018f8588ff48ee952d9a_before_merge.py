def collection_delete(request, pk=None):
    collection = get_object_or_404(Collection, pk=pk)
    if request.method == "POST":
        menus = get_menus_that_needs_update(collection=collection)
        collection.delete()
        if menus:
            update_menus(menus)
        msg = pgettext_lazy("Collection message", "Deleted collection")
        messages.success(request, msg)
        if request.is_ajax():
            response = {"redirectUrl": reverse("dashboard:collection-list")}
            return JsonResponse(response)
        return redirect("dashboard:collection-list")
    ctx = {"collection": collection}
    return TemplateResponse(request, "dashboard/collection/confirm_delete.html", ctx)