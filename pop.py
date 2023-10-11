import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def initialize_driver(headless=False):
    options = Options()
    options.add_argument("--detached")
    if headless:
        options.add_argument("--headless")

    return webdriver.Chrome(options=options)


def verify_login(driver, locator, cred):
    time.sleep(5)
    element = driver.find_elements(By.CSS_SELECTOR, locator)
    if not element:
        print("trying to login")
        login(driver, cred)
        verify_login(driver, locator, cred)
    else:
        print("locator found!")
        return True


def login(driver, cred):
    user = driver.find_element(By.CSS_SELECTOR, "input[id = 'email']")
    user.send_keys(cred["usr"])
    time.sleep(1)
    user = driver.find_element(By.CSS_SELECTOR, "input[id = 'password']")
    user.send_keys(cred["pwd"])
    time.sleep(1)
    user = driver.find_element(By.CSS_SELECTOR, "button[type = 'submit']")
    user.click()
    time.sleep(5)


def access_product(driver, product_hash, cred):
    try:
        # Open the product edit page
        driver.get(f"https://accounts.yupop.com/login")
        time.sleep(2)
        login(driver, cred)
        time.sleep(5)
        input("Press Enter to continue...")
        print("logged in")
        driver.get(f"https://www.posterage.com/admin/catalogue/products/edit/{product_hash}")

    finally:
        # return driver
        return driver


def mine(driver):
    info = {}
    info["url"] = driver.current_url
    info["hash"] = driver.current_url.replace("https://www.posterage.com/admin/catalogue/products/edit/", "")
    info["Nombre"] = driver.find_element(By.CSS_SELECTOR, "input[name = 'name']").get_attribute("value")

    # iframe
    iframe_element = driver.find_element(By.CSS_SELECTOR, "iframe[title = 'Rich Text Area']")
    driver.switch_to.frame(iframe_element)
    info["Descripción"] = driver.find_element(By.CSS_SELECTOR, "body[id = 'tinymce']").find_element(By.TAG_NAME,
                                                                                                    "p").text
    driver.switch_to.default_content()

    album = driver.find_elements(By.CSS_SELECTOR, "figure[class = 'sc-kjUpzh jEwzPv']")
    info["Fotografías"] = []
    for foto in album:
        info["Fotografías"].append("https://www.posterage.com" + foto.get_attribute("src"))

    caract = driver.find_elements(By.CSS_SELECTOR, "textarea[class = 'sc-idvBfp fnPvlx']")
    info["Características"] = []
    for destaque in caract:
        info["Características"].append(destaque.get_attribute("id"))

    # TODO: Universalizar
    info["Categoría"] = "TIENDA"
    info["Marca"] = ""

    # Variantes TODO: Universalizar
    var_check = driver.find_elements(By.CSS_SELECTOR, "section[class = 'sc-vdgyJ jcOiBB']")
    if var_check:
        variantes = driver.find_elements(By.CSS_SELECTOR, "div[class = 'sc-fZUakH cvFGs']")
        info["Variantes"] = []
        info["Stock"] = []
        i = 0
        for vari in variantes:
            info["Variantes"].append(vari.text)
            info["Stock"].append(driver.find_element(By.CSS_SELECTOR,
                                                     f"input[id = 'product-varant-variants[{i}].availability.stock-stock']").get_attribute(
                "value"))

    # Mismo precio por variante
    if driver.find_elements(By.CSS_SELECTOR, "input[id = 'product-same-price']"):
        mismo_precio_por_variante = driver.find_element(By.CSS_SELECTOR, "input[id = 'product-same-price']")
        if mismo_precio_por_variante.get_attribute("outerHTML").find("checked") != -1:
            info["Mismo_precio_por_variante"] = "True"
        else:
            info["Mismo_precio_por_variante"] = "False"
    else:
        info["Mismo_precio_por_variante"] = "None"

    precios_fixos = driver.find_elements(By.CSS_SELECTOR, "div[label = '€']")
    info["Precio"] = []
    info["Oferta"] = []
    if precios_fixos:
        i = 0
        for precios in precios_fixos:
            if precios.find_element(By.CSS_SELECTOR, "input").get_attribute("id").find("discountlessPrice") != -1:
                print("Precio found!")
                info["Precio"].append(precios.find_element(By.CSS_SELECTOR, "input").get_attribute("value"))
                i = i + 1
            elif precios.find_element(By.CSS_SELECTOR, "input").get_attribute("id").find("discountedPrice") != -1:
                print("Oferta found!")
                info["Oferta"].append(precios.find_element(By.CSS_SELECTOR, "input").get_attribute("value"))
                i = i + 1
            else:
                print("Precio not found!")
                info["Precio"].append("?")
                info["Oferta"].append("?")
                i = i + 1

    compra_sin_stock = driver.find_elements(By.CSS_SELECTOR, "input[id = 'product-allow-no-stock-buy']")
    if compra_sin_stock:
        info["Compra Sin Stock"] = ""
        if compra_sin_stock[0].get_attribute("outerHTML").find("checked") != -1:
            info["Compra Sin Stock"] = "True"
            info["Tiempo Adicional"] = driver.find_element(By.CSS_SELECTOR, "input[id = 'product-no-stock-days']").get_attribute(
                "value")
        else:
            info["Compra Sin Stock"] = "False"

    pesos = driver.find_elements(By.CSS_SELECTOR, "input[type = 'number']")
    info["Peso"] = []
    for peso in pesos:
        if peso.get_attribute("outerHTML").find("weight") != -1:
            print(peso.get_attribute("value"))
            info["Peso"].append(peso.get_attribute("value"))
            break
    altos = driver.find_elements(By.CSS_SELECTOR, "input[type = 'number']")
    info["Alto"] = []
    for alto in altos:
        if alto.get_attribute("id").find("height") != -1:
            info["Alto"].append(alto.get_attribute("value"))
            break
    anchos = driver.find_elements(By.CSS_SELECTOR, "input[type = 'number']")
    info["Ancho"] = []
    for ancho in anchos:
        if ancho.get_attribute("id").find("width") != -1:
            info["Ancho"].append(ancho.get_attribute("value"))
            break
    fondos = driver.find_elements(By.CSS_SELECTOR, "input[type = 'number']")
    info["Fondo"] = []
    for fondo in fondos:
        if fondo.get_attribute("id").find("depth") != -1:
            info["Fondo"].append(fondo.get_attribute("value"))
            break

    visible = driver.find_elements(By.CSS_SELECTOR, "input[id = 'product-enabled']")
    if visible:
        info["Visible"] = ""
        if visible[0].get_attribute("outerHTML").find("checked") != -1:
            info["Visible"] = "True"
        else:
            info["Visible"] = "False"

    with open(f"Cloner/{info['hash']}", 'w', encoding='utf-8') as json_file:
        json.dump(info, json_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    keys = {"usr": "toni.tort92@gmail.com", "pwd": "Superantonio92!"}
    driver1 = initialize_driver()
    access_product(driver1, "78ab7b37-f3ab-4da4-ab9a-50329e62095a", keys)
    input("Press Enter to mine...")
    mine(driver1)

    input("Press Enter to close the browser...")
