import json
import os
import time
import urllib.request

import pyautogui
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from slugify import slugify


def initialize_driver():
    # return webdriver.Firefox(options=options)
    print("initializing driver")
    return webdriver.Firefox()


def login(cred, driver=None):
    try:
        if driver is None:
            driver = initialize_driver()

        # Login page
        if driver.current_url != "https://accounts.yupop.com/login":
            driver.get(f"https://accounts.yupop.com/login")
            time.sleep(2)
        if driver.current_url == "https://accounts.yupop.com/login":
            print("login page")
            user = driver.find_elements(By.CSS_SELECTOR, "input[id = 'email']")
            if user:
                user[0].send_keys(cred["usr"])
                password = driver.find_element(By.CSS_SELECTOR, "input[id = 'password']")
                password.send_keys(cred["pwd"])
                btn = driver.find_element(By.CSS_SELECTOR, "button[type = 'submit']")
                btn.click()
                time.sleep(5)
                if driver.current_url.find("https://accounts.yupop.com/login") == -1:
                    print("login successful")
                else:
                    print("login failed")
            else:
                time.sleep(5)
                user = driver.find_elements(By.CSS_SELECTOR, "input[id = 'email']")
                if user:
                    login(cred, driver)

    except Exception as e:
        print("Exception on login:\n")
        print(e)
    finally:
        # return driver
        time.sleep(5)
        return driver


def mine(driver, product_url=None):
    global info
    try:
        if product_url is None:
            product_url = driver.current_url
        elif product_url.find("https://www.posterage.com/admin/catalogue/products/edit/") != -1:
            driver.get(product_url)
        else:
            raise Exception("Product URL is not valid")
        time.sleep(2)

        # check
        if driver.find_elements(By.CSS_SELECTOR, "input[id = 'product-enabled']"):
            print("Starting data miner.")
            info = {}
            info["url"] = driver.current_url
            info["hash"] = driver.current_url.replace("https://www.posterage.com/admin/catalogue/products/edit/", "")
            info["Nombre"] = driver.find_element(By.CSS_SELECTOR, "input[name = 'name']").get_attribute(
                "value").replace(" ", "_")

            # iframe
            print("Bypassing iframe.")
            iframe_element = driver.find_element(By.CSS_SELECTOR, "iframe[title = 'Rich Text Area']")
            driver.switch_to.frame(iframe_element)
            info["Descripción"] = driver.find_element(By.CSS_SELECTOR, "body[id = 'tinymce']").find_element(By.TAG_NAME,
                                                                                                            "p").text
            print("Switching back from iframe.")
            driver.switch_to.default_content()

            print("Searching for images.")
            album = driver.find_elements(By.CSS_SELECTOR, "figure[class = 'sc-kjUpzh jEwzPv']")
            info["Fotografías"] = []
            for foto in album:
                info["Fotografías"].append("https://www.posterage.com" + foto.get_attribute("src"))

            print("Searching for features.")
            caract = driver.find_elements(By.CSS_SELECTOR, "textarea[class = 'sc-idvBfp fnPvlx']")
            info["Características"] = []
            for destaque in caract:
                info["Características"].append(destaque.get_attribute("id"))

            # TODO: Universalizar
            info["Categoría"] = "TIENDA"
            info["Marca"] = ""

            # Variantes TODO: Universalizar
            print("Searching for variants.")
            var_check = driver.find_elements(By.CSS_SELECTOR, "section[class = 'sc-vdgyJ jcOiBB']")
            if var_check:
                variantes = driver.find_elements(By.CSS_SELECTOR, "div[class = 'sc-fZUakH cvFGs']")
                info["Variantes"] = []
                info["Stock"] = []
                i = 0
                for vari in variantes:
                    info["Variantes"].append(vari.text)
                    info["Stock"].append(driver.find_element(By.CSS_SELECTOR,
                                                             f"input[id = 'product-varant-variants[{i}].availability.stock"
                                                             f"-stock']").get_attribute(
                        "value"))

            # Mismo precio por variante
            print("Searching for same price opt.")
            if driver.find_elements(By.CSS_SELECTOR, "input[id = 'product-same-price']"):
                mismo_precio_por_variante = driver.find_element(By.CSS_SELECTOR, "input[id = 'product-same-price']")
                if mismo_precio_por_variante.get_attribute("outerHTML").find("checked") != -1:
                    info["Mismo_precio_por_variante"] = "True"
                else:
                    info["Mismo_precio_por_variante"] = "False"
            else:
                info["Mismo_precio_por_variante"] = "None"

            print("Searching for prices.")
            precios_fixos = driver.find_elements(By.CSS_SELECTOR, "div[label = '€']")
            info["Precio"] = []
            info["Oferta"] = []
            if precios_fixos:
                i = 0
                for precios in precios_fixos:
                    if precios.find_element(By.CSS_SELECTOR, "input").get_attribute("id").find(
                            "discountlessPrice") != -1:
                        print("Precio found!")
                        info["Precio"].append(precios.find_element(By.CSS_SELECTOR, "input").get_attribute("value"))
                        i = i + 1
                    elif precios.find_element(By.CSS_SELECTOR, "input").get_attribute("id").find(
                            "discountedPrice") != -1:
                        print("Oferta found!")
                        info["Oferta"].append(precios.find_element(By.CSS_SELECTOR, "input").get_attribute("value"))
                        i = i + 1
                    else:
                        print("Precio not found!")
                        info["Precio"].append("?")
                        info["Oferta"].append("?")
                        i = i + 1

            print("Searching for stock.")
            compra_sin_stock = driver.find_elements(By.CSS_SELECTOR, "input[id = 'product-allow-no-stock-buy']")
            if compra_sin_stock:
                info["Compra Sin Stock"] = ""
                if compra_sin_stock[0].get_attribute("outerHTML").find("checked") != -1:
                    info["Compra Sin Stock"] = "True"
                    info["Tiempo Adicional"] = driver.find_element(By.CSS_SELECTOR,
                                                                   "input[id = 'product-no-stock-days']").get_attribute(
                        "value")
                else:
                    info["Compra Sin Stock"] = "False"

            print("Searching for dimensions.")
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

            print("Searching for visibility.")
            visible = driver.find_elements(By.CSS_SELECTOR, "input[id = 'product-enabled']")
            if visible:
                info["Visible"] = ""
                if visible[0].get_attribute("outerHTML").find("checked") != -1:
                    info["Visible"] = "True"
                else:
                    info["Visible"] = "False"

            with open(f"Cloner/{slugify(info['Nombre'])}", 'w', encoding='utf-8') as json_file:
                json.dump(info, json_file, ensure_ascii=False, indent=4)
        else:
            print("can't find product page | waiting a little more...")
            time.sleep(5)
            if driver.find_elements(By.CSS_SELECTOR, "input[id = 'product-enabled']"):
                mine(driver)
    except Exception as e:
        print(e)

    finally:
        return f"{slugify(info['Nombre'])}"


def creator(driver, file, is_visible=bool, has_images=bool):
    driver.get("https://www.posterage.com/admin/catalogue/products/create")
    time.sleep(2)
    print(f"Loading product data from {file}.")
    with open(f"Cloner/{file}", 'r', encoding='utf-8') as json_file:
        product = json.load(json_file)

    print("Writing data.")
    # name
    product_name = driver.find_elements(By.CSS_SELECTOR, "input")
    if product_name:
        for input in product_name:
            if input.get_attribute("id").find("product-name") != -1:
                input.send_keys(product["Nombre"])
                break

    # iframe
    print("Bypassing iframe again.")
    product_desc = driver.find_elements(By.CSS_SELECTOR, "iframe")
    if product_desc:
        for input in product_desc:
            if input.get_attribute("id").find("tiny-react") != -1:
                driver.switch_to.frame(input)
                box = driver.find_element(By.CSS_SELECTOR, "body[id = 'tinymce']")
                box.click()
                box.send_keys(product["Descripción"])
                driver.switch_to.default_content()
                break
    print("Back from iframe.")

    if has_images:
        print("Downloading images.")
        # pics
        fotos = product["Fotografías"]
        img_path = []
        i = 0
        for fotourl in fotos:
            print("Downloading " + fotourl)
            print(f"{i}/{len(fotos)}")
            img_path.append(urllib.request.urlretrieve(fotourl, f"Cloner/img/img{i}.png")[0])
            print(img_path[i])
            i = i + 1

        # upload
        ospath = os.getcwd()
        bt = driver.find_elements(By.CSS_SELECTOR, "button")
        if bt:
            for button in bt:
                if button.get_attribute("class").find("sc-dyTUbJ dKjDkb") != -1:
                    for img in img_path:
                        button.send_keys(Keys.ENTER)
                        time.sleep(2)
                        pyautogui.write(ospath)
                        time.sleep(2)
                        pyautogui.press('enter')
                        time.sleep(2)
                        pyautogui.write(img.replace('/', '\\'))
                        time.sleep(2)
                        pyautogui.press('enter')
                        time.sleep(2)
                    break

        # delete
        print("Deleting images from pc.")
        for path in img_path:
            print("Deleting " + ospath + "\\" + path.replace('/', '\\'))
            os.remove(path)

    # Características
    print("Adding features.")
    carac = product["Características"]
    btn = driver.find_elements(By.CSS_SELECTOR, "button[class = 'sc-ewnqHT bVbYNJ']")
    if btn:
        i = 0
        for car in carac:
            btn[0].send_keys(Keys.ENTER)
            txtarea = driver.find_elements(By.CSS_SELECTOR, "textarea")
            for input in txtarea:
                if input.get_attribute("name").find(f"features[{i}]") != -1:
                    input.send_keys(car)
                    i = i + 1
                    break

    # Category
    cat = product["Categoría"]
    btn = driver.find_elements(By.CSS_SELECTOR, "input[class = 'react-select__input']")
    if btn:
        btn[0].send_keys(cat)
        time.sleep(2)
        btn[0].send_keys(Keys.ENTER)

    # TODO: Marca

    # variantes
    var = product["Variantes"]
    btn = driver.find_elements(By.CSS_SELECTOR, "button[class = 'sc-ewnqHT iPHMCZ']")
    if btn:
        btn[1].send_keys(Keys.ENTER)
        driver.find_element(By.CSS_SELECTOR, "nav[class = 'sc-kGRGSO jyEHoA']").find_element(By.CSS_SELECTOR,
                                                                                             "button").send_keys(
            Keys.ENTER)
        time.sleep(1)
        tams = driver.find_elements(By.CSS_SELECTOR, "label[class = 'sc-hQPFnu jnXvvm']")
        for tam in tams:
            tam.click()
            time.sleep(0.5)
        aceptar = driver.find_elements(By.CSS_SELECTOR, "footer[class = 'sc-gACFrS hFAfWs']")
        if aceptar:
            aceptar[0].find_elements(By.CSS_SELECTOR, "button")[0].click()
            time.sleep(1)

    # mismo precio por variante
    mismo_precio = product["Mismo_precio_por_variante"]
    btn = driver.find_elements(By.CSS_SELECTOR, "input[id = 'product-same-price']")
    if btn:
        if btn[0].get_attribute("outerHTML").find("checked") != -1:
            if mismo_precio == "False":
                btn[0].click()
                time.sleep(1)
        else:
            if mismo_precio == "True":
                btn[0].click()
                time.sleep(1)

    # stock
    print("Adding stock.")
    if mismo_precio == "True":
        stock = product["Stock"]
        i = 0
        for stock in stock:
            input = driver.find_elements(By.CSS_SELECTOR, "input[type = 'number']")
            for input in input:
                if input.get_attribute("outerHTML").find(f"variants[{i}].availability.stock") != -1:
                    input.send_keys(stock)
                    i = i + 1
                    break

    # dimensiones
    print("Adding dimensions.")
    if mismo_precio:
        precio = product["Precio"]
        if precio:
            input = driver.find_elements(By.CSS_SELECTOR, "input[type = 'number']")
            for input in input:
                if input.get_attribute("outerHTML").find("discountless") != -1:
                    input.send_keys(precio[0])
                    break
        oferta = product["Oferta"]
        if oferta:
            input = driver.find_elements(By.CSS_SELECTOR, "input[type = 'number']")
            for input in input:
                if input.get_attribute("outerHTML").find("discounted") != -1:
                    input.send_keys(oferta[0])
                    break
        peso = product["Peso"]
        if peso:
            input = driver.find_elements(By.CSS_SELECTOR, "input[type = 'number']")
            for input in input:
                if input.get_attribute("outerHTML").find("variants[0].weight") != -1:
                    input.send_keys(peso[0])
                    break
        alto = product["Alto"]
        if alto:
            input = driver.find_elements(By.CSS_SELECTOR, "input[type = 'number']")
            for input in input:
                if input.get_attribute("outerHTML").find("height") != -1:
                    input.send_keys(alto[0])
                    break
        ancho = product["Ancho"]
        if ancho:
            input = driver.find_elements(By.CSS_SELECTOR, "input[type = 'number']")
            for input in input:
                if input.get_attribute("outerHTML").find("width") != -1:
                    input.send_keys(ancho[0])
                    break
        fondo = product["Fondo"]
        if fondo:
            input = driver.find_elements(By.CSS_SELECTOR, "input[type = 'number']")
            for input in input:
                if input.get_attribute("outerHTML").find("depth") != -1:
                    input.send_keys(fondo[0])
                    break
    # TODO: testar mismo_precio false
    else:
        peso = product["Peso"]
        if peso:
            input = driver.find_elements(By.CSS_SELECTOR, "input[type = 'number']")
            i = 0
            for peso in peso:
                for input in input:
                    if input.get_attribute("outerHTML").find(f"variants[{i}].weight") != -1:
                        input.send_keys(peso)
                        i = i + 1
                        break

    # visivel TODO: testar
    visi = is_visible
    blocked = True
    edited = False
    while blocked:
        try:
            if visi:
                input = driver.find_elements(By.CSS_SELECTOR, "input[id = 'product-enabled']")
                for input in input:
                    if input.get_attribute("outerHTML").find("checked") != -1:
                        blocked = False
                        if edited:
                            driver.execute_script("document.getElementsByTagName('footer').style.display = 'grid';")
                            edited = False
                        break
                    else:
                        input.send_keys(Keys.SPACE)
                        print("Visible clicked")
                        blocked = False
                        if edited:
                            driver.execute_script("document.getElementsByTagName('footer').style.display = 'grid';")
                            edited = False
                        break
            else:
                input = driver.find_elements(By.CSS_SELECTOR, "input[id = 'product-enabled']")
                for input in input:
                    if input.get_attribute("outerHTML").find("checked") != -1:
                        input.send_keys(Keys.SPACE)
                        print("Visible clicked")
                        blocked = False
                        if edited:
                            driver.execute_script("document.getElementsByTagName('footer').style.display = 'grid';")
                            edited = False
                        break
                    else:
                        blocked = False
                        if edited:
                            driver.execute_script("document.getElementsByTagName('footer').style.display = 'grid';")
                            edited = False
                        break
        except:
            print("blocked")
            driver.execute_script("document.getElementsByTagName('footer').style.display = 'none';")
            edited = True

    # guardar

    blocked = True
    edited = False
    while blocked:
        try:
            button = driver.find_elements(By.CSS_SELECTOR, "button[type = 'submit']")
            print(len(button))
            button[0].click()
            blocked = False
        except:
            print("blocked")
            script = """
            e = document.getElementsByClassName('sc-kJpdyg fCbVSs')[0];
            e.style.display = 'none';
            """
            driver.execute_script(script)
            edited = True

    while 1:
        time.sleep(1)
        if driver.current_url != "www.posterage.com/admin/catalogue/products/create":
            break
