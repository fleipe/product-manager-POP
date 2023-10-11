import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains


def initialize_driver(headless=False):
    """
    The initialize_driver function initializes a Chrome webdriver instance with the following options:
            - --detached: This option allows the driver to stay open after the script has finished, while debugging.

        :return: A webdriver object

    :return: A webdriver object
    :doc-author: Felipe Linares
    """

    options = Options()
    options.add_argument("--detached")
    if headless:
        options.add_argument("--headless")

    return webdriver.Chrome(options=options)


def access_tibia(driver):
    """
    The access_tibia function opens the TIBIA website and returns the driver object.

    :param driver: Webdriver
    :return: The driver
    :doc-author: Felipe Linares
    """
    try:
        # Open the TIBIA website
        driver.get("https://www.tibia.com/community/?subtopic=houses")

    finally:
        # return driver
        return driver


def select_world(driver, world_query, town_query):
    """
    The select_world function takes in a driver and two queries, one for the world and one for the town. It then
    navigates to tibia.com/community/?subtopic=worlds, selects the appropriate world from a dropdown menu,
    selects an appropriate town from another dropdown menu (if there is more than one), clicks on &quot;Rented
    Houses&quot; and submits all of this information to navigate to that specific world's rented houses page.

    :param driver: Access the webdriver
    :param world_query: Select the world that you want to search for houses in
    :param town_query: Select the town that you want to search for houses in
    :return: The driver with the new tab open
    :doc-author: Felipe Linares
    """
    driver = access_tibia(driver)

    # Get Elements
    windows = driver.window_handles
    driver.switch_to.window(windows[0])
    world_bar = driver.find_element(By.NAME, "world")
    towns = driver.find_elements(By.NAME, "town")
    rented = driver.find_element(By.CSS_SELECTOR,
                                 'div#houses > div:nth-of-type(5) > div > div > form > div > table > tbody > tr > td '
                                 '> div:nth-of-type(2) > table > tbody > tr:nth-of-type(2) > td > div > table > tbody '
                                 '> tr:nth-of-type(2) > td:nth-of-type(2) > label:nth-of-type(3) > input')
    submit = driver.find_element(By.CSS_SELECTOR, "input[value = 'Submit']")

    # Perform actions
    rented.click()

    world_bar.send_keys(world_query + Keys.ENTER)
    for town in towns:
        print(town.get_attribute("value") + "is the town")
        if town.get_attribute("value") == town_query:
            town.click()
            submit.click()
            time.sleep(1)
            navigate(driver, world_query)
            break

    return driver


def navigate(driver, world_query):
    """
    The navigate function takes in a driver and world_query as parameters.
    It then creates an ActionChains object to perform actions on the web page.
    The function finds all the &quot;View&quot; buttons on the page, clicks them, and
    then navigates through each tab that opens up to find any text that contains
    the phrase &quot;passed by house&quot;. If it does find this phrase, it writes this text
    to a file called moving_out_{world_query}.txt.

    :param driver: Pass the driver object to the function
    :param world_query: Specify which world to search for
    :return: The content of the views
    :doc-author: Felipe Linares
    """
    actions = ActionChains(driver)

    # Get Views
    views = driver.find_elements(By.CSS_SELECTOR, "input[value = 'View']")

    # Click views
    for view in views:
        time.sleep(1)
        actions.key_down(Keys.CONTROL).click(view).key_up(Keys.CONTROL).perform()

        # Navigate tabs
        windows = driver.window_handles

        for window in windows:
            driver.switch_to.window(window)
            if driver.find_elements(By.CSS_SELECTOR, "input[value = 'Back']"):
                content = driver.find_elements(By.TAG_NAME, "td")[1].text
                with open("output_" + world_query + ".txt", "a") as f:
                    f.write(content + "\n\n ---------------------------------------\n\n")
                print(content)
                if "pass the house" in content:
                    with open("moving_out_" + world_query + ".txt", "a", encoding="utf-8") as f:
                        f.write(content + "\n\n ---------------------------------------\n\n")
                driver.close()
                driver.switch_to.window(windows[0])
                break


# Example usage
def main():
    """
    The main function is the entry point of the program.
    It initializes a driver, selects a world and town, and then quits.

    :return: The driver
    :doc-author: Felipe Linares
    """
    with open("Towns", "r") as f:
        towns = f.readlines()
    with open("Worlds", "r") as f:
        worlds = f.readlines()

    for world in worlds:
        for town in towns:
            print(town)
            driver1 = initialize_driver()
            driver1 = select_world(driver1, world.rstrip("\n"), town.rstrip("\n"))
            driver1.quit()
    input("Press Enter to close the browser...")


if __name__ == "__main__":
    main()
