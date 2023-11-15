def follow_user(browser, follow_restrict, login, user_name):
    """Follows the user of the currently opened image"""

    try:
        follow_button = browser.find_element_by_xpath("//*[contains(text(), 'Follow')]")
        
        sleep(2) # Do we still need this sleep?
        if follow_button.is_displayed():
            follow_button.send_keys("\n")
        else:
            driver.execute_script("arguments[0].style.visibility = 'visible'; arguments[0].style.height = '10px'; arguments[0].style.width = '10px'; arguments[0].style.opacity = 1", follow_button)
            follow_button.click()
        
        print('--> Now following')
        log_followed_pool(login, user_name)
        follow_restrict[user_name] = follow_restrict.get(user_name, 0) + 1
        sleep(3)
        return 1
    except NoSuchElementException:
        print('--> Already following')
        sleep(1)
        return 0