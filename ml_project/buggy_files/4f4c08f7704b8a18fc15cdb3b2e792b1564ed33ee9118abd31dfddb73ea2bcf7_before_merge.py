def select_sheets(title='Select Sheets',
                  button_name='Select',
                  width=DEFAULT_INPUTWINDOW_WIDTH,
                  multiple=True,
                  filterfunc=None,
                  doc=None):
    """Standard form for selecting sheets.

    Sheets are grouped into sheet sets and sheet set can be selected from
    a drop down box at the top of window.

    Args:
        title (str, optional): list window title
        button_name (str, optional): list window button caption
        width (int, optional): width of list window
        multiselect (bool, optional):
            allow multi-selection (uses check boxes). defaults to True
        filterfunc (function):
            filter function to be applied to context items.
        doc (DB.Document, optional):
            source document for sheets; defaults to active document

    Returns:
        list[DB.ViewSheet]: list of selected sheets

    Example:
        >>> from pyrevit import forms
        >>> forms.select_sheets()
        ... [<Autodesk.Revit.DB.ViewSheet object>,
        ...  <Autodesk.Revit.DB.ViewSheet object>]
    """
    doc = doc or HOST_APP.doc
    all_ops = dict()
    all_sheets = DB.FilteredElementCollector(doc) \
                   .OfClass(DB.ViewSheet) \
                   .WhereElementIsNotElementType() \
                   .ToElements()

    if filterfunc:
        all_sheets = filter(filterfunc, all_sheets)

    all_sheets_ops = sorted([SheetOption(x) for x in all_sheets],
                            key=lambda x: x.number)
    all_ops['All Sheets'] = all_sheets_ops

    sheetsets = revit.query.get_sheet_sets(doc)
    for sheetset in sheetsets:
        sheetset_sheets = sheetset.Views
        if filterfunc:
            sheetset_sheets = filter(filterfunc, sheetset_sheets)
        sheetset_ops = sorted([SheetOption(x) for x in sheetset_sheets],
                              key=lambda x: x.number)
        all_ops[sheetset.Name] = sheetset_ops

    # ask user for multiple sheets
    selected_sheets = SelectFromList.show(
        all_ops,
        title=title,
        group_selector_title='Sheet Sets:',
        button_name=button_name,
        width=width,
        multiselect=multiple,
        checked_only=True
        )

    return selected_sheets