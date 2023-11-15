def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        descendants = category.get_descendants()
        menus = get_menus_that_need_update(categories=descendants)
        category.delete()
        if menus:
            update_menus(menus)
        messages.success(
            request,
            pgettext_lazy("Dashboard message", "Removed category %s") % category,
        )
        root_pk = None
        if category.parent:
            root_pk = category.parent.pk
        if root_pk:
            if request.is_ajax():
                response = {
                    "redirectUrl": reverse(
                        "dashboard:category-details", kwargs={"pk": root_pk}
                    )
                }
                return JsonResponse(response)
            return redirect("dashboard:category-details", pk=root_pk)
        else:
            if request.is_ajax():
                response = {"redirectUrl": reverse("dashboard:category-list")}
                return JsonResponse(response)
            return redirect("dashboard:category-list")
    ctx = {
        "category": category,
        "descendants": list(category.get_descendants()),
        "products_count": len(category.products.all()),
    }
    return TemplateResponse(
        request, "dashboard/category/modal/confirm_delete.html", ctx
    )