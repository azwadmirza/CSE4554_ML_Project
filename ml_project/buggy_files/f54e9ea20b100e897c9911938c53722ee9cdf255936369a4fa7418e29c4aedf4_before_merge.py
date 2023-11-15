def get_elements_by_categories(element_bicats, elements=None, doc=None):
    # if source elements is provided
    if elements:
        return [x for x in elements
                if get_builtincategory(x.Category.Name)
                in element_bicats]

    # otherwise collect from model
    cat_filters = [DB.ElementCategoryFilter(x) for x in element_bicats]
    elcats_filter = \
        DB.LogicalOrFilter(framework.List[DB.ElementFilter](cat_filters))
    return DB.FilteredElementCollector(doc or HOST_APP.doc)\
             .WherePasses(elcats_filter)\
             .WhereElementIsNotElementType()\
             .ToElements()