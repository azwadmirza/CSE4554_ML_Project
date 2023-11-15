def _get_msi_software():
    '''
    This searches the msi product databases and returns a dict keyed
    on the product name and all the product properties in another dict
    '''
    win32_products = {}
    this_computer = "."
    wmi_service = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    swbem_services = wmi_service.ConnectServer(this_computer, "root\\cimv2")
    products = swbem_services.ExecQuery("Select * from Win32_Product")
    for product in products:
        try:
            prd_name = product.Name.encode('ascii', 'ignore')
            prd_ver = product.Version.encode('ascii', 'ignore')
            win32_products[prd_name] = prd_ver
        except Exception:
            pass
    return win32_products