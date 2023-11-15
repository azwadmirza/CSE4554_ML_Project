def modify_database_object(input_elements, db_book_object, db_object, db_session, db_type):
    # passing input_elements not as a list may lead to undesired results
    if not isinstance(input_elements, list):
        raise TypeError(str(input_elements) + " should be passed as a list")

    input_elements = [x for x in input_elements if x != '']
    # we have all input element (authors, series, tags) names now
    # 1. search for elements to remove
    del_elements = []
    for c_elements in db_book_object:
        found = False
        if db_type == 'languages':
            type_elements = c_elements.lang_code
        elif db_type == 'custom':
            type_elements = c_elements.value
        else:
            type_elements = c_elements.name
        for inp_element in input_elements:
            if inp_element.lower() == type_elements.lower():
                found = True
                break
        # if the element was not found in the new list, add it to remove list
        if not found:
            del_elements.append(c_elements)
    # 2. search for elements that need to be added
    add_elements = []
    for inp_element in input_elements:
        found = False
        for c_elements in db_book_object:
            if db_type == 'languages':
                type_elements = c_elements.lang_code
            elif db_type == 'custom':
                type_elements = c_elements.value
            else:
                type_elements = c_elements.name
            if inp_element == type_elements:
                found = True
                break
        if not found:
            add_elements.append(inp_element)
    # if there are elements to remove, we remove them now
    if len(del_elements) > 0:
        for del_element in del_elements:
            db_book_object.remove(del_element)
            if len(del_element.books) == 0:
                db_session.delete(del_element)
    # if there are elements to add, we add them now!
    if len(add_elements) > 0:
        if db_type == 'languages':
            db_filter = db_object.lang_code
        elif db_type == 'custom':
            db_filter = db_object.value
        else:
            db_filter = db_object.name
        for add_element in add_elements:
            # check if a element with that name exists
            db_element = db_session.query(db_object).filter(db_filter == add_element).first()
            # if no element is found add it
            # if new_element is None:
            if db_type == 'author':
                new_element = db_object(add_element, helper.get_sorted_author(add_element.replace('|', ',')), "")
            elif db_type == 'series':
                new_element = db_object(add_element, add_element)
            elif db_type == 'custom':
                new_element = db_object(value=add_element)
            elif db_type == 'publisher':
                new_element = db_object(add_element, None)
            else:  # db_type should be tag or language
                new_element = db_object(add_element)
            if db_element is None:
                db_session.add(new_element)
                db_book_object.append(new_element)
            else:
                if db_type == 'custom' and db_element.value != add_element:
                    new_element.value = add_element
                    # new_element = db_element
                elif db_type == 'language' and db_element.lang_code != add_element:
                    db_element.lang_code = add_element
                    # new_element = db_element
                elif db_type == 'series' and db_element.name != add_element:
                    db_element.name = add_element # = add_element # new_element = db_object(add_element, add_element)
                    db_element.sort = add_element
                    # new_element = db_element
                elif db_type == 'author' and db_element.name != add_element:
                    db_element.name = add_element
                    db_element.sort = add_element.replace('|', ',')
                    # new_element = db_element
                if db_type == 'publisher' and db_element.name != add_element:
                    db_element.name = add_element
                    db_element.sort = None
                    # new_element = db_element
                elif db_element.name != add_element:
                    db_element.name = add_element
                    # new_element = db_element
                # add element to book
                db_book_object.append(db_element)