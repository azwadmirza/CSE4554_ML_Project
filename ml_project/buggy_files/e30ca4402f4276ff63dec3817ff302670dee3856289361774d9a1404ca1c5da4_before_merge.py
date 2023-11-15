def follow_user(browser, follow_restrict, login, user_name):
    """Follows the user of the currently opened image"""

    try:
        follow_button = browser.find_element_by_xpath("//*[contains(text(), 'Follow')]")
        sleep(2) # Do we still need this sleep?
        follow_button.send_keys("\n")
        
        print('--> Now following')
        log_followed_pool(login, user_name)
        follow_restrict[user_name] = follow_restrict.get(user_name, 0) + 1
        sleep(3)
        return 1
    except NoSuchElementException:
        print('--> Already following')
        sleep(1)
        return 0