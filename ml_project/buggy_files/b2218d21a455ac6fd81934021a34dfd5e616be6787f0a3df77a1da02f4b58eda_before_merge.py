def install_product(app, product_dir, product_name, meta_types,
                    folder_permissions, raise_exc=None):
    if not _is_package(product_dir, product_name):
        return

    __traceback_info__ = product_name
    global_dict = globals()
    product = __import__("Products.%s" % product_name,
                         global_dict, global_dict, ('__doc__', ))

    # Install items into the misc_ namespace, used by products
    # and the framework itself to store common static resources
    # like icon images.
    misc_ = pgetattr(product, 'misc_', {})
    if misc_:
        if isinstance(misc_, dict):
            misc_ = Misc_(product_name, misc_)
        Application.misc_.__dict__[product_name] = misc_

    productObject = FactoryDispatcher.Product(product_name)
    context = ProductContext(productObject, None, product)

    # Look for an 'initialize' method in the product.
    initmethod = pgetattr(product, 'initialize', None)
    if initmethod is not None:
        initmethod(context)