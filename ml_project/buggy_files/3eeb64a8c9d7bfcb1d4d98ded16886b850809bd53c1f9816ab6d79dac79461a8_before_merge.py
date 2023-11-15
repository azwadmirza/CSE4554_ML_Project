def log_list_finished(links):
    print()
    print('---------------------------------------------------------------------------------------------------')
    print(links_to_csv(links, cols=['timestamp', 'is_archived', 'num_outputs', 'url'], header=True, ljust=16, separator=' | '))
    print('---------------------------------------------------------------------------------------------------')
    print()