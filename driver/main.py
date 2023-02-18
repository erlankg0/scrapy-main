import json
import os
import time
import urllib.request

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from transliterate import translit

# Create a Service object with the path to the Chrome driver executable
service = Service('C:\\Users\\User\\PycharmProjects\\scrapy\\driver\\chromedriver.exe')

# Start the Chrome driver, passing in the Service object
driver = webdriver.Chrome(service=service)

# Rest of your code...

options = webdriver.ChromeOptions()
ua = UserAgent()
userAgent = ua.random
options.add_argument(f'user-agent={userAgent}')
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-notifications")
options.add_argument("--disable-infobars")
driver = webdriver.Chrome(
    executable_path="C:\\Users\\User\\PycharmProjects\\scrapy\\driver\\chromedriver.exe",
    options=options
)


def get_brands():
    # get all brands class name = "mark__item"
    try:
        driver.get("https://franko-auto.ru/cars/")
        # get all brands class name = "mark__item"
        brands = driver.find_elements("class name", "mark__item")
        # save all brands url in JSON file {"brands": ["name": "brand_name", "url": "brand_url"] }
        brands_url = {
            "brands": [{"name": brand.text, "url": brand.find_element("class name", "mark__link").get_attribute("href")}
                       for
                       brand in brands]  # list comprehension

        }
        with open("brands.json", "w") as f:
            json.dump(brands_url, f)
        for brand in brands:
            # create a folder with the name of the brand use import os in current directory
            if not os.path.exists(brand.text):
                os.mkdir(brand.text)
            # download img of the brand and save it in the folder
            wait = WebDriverWait(driver, 10)
            img = brand.find_element("class name", "lazy")
            urllib.request.urlretrieve(img.get_attribute("src"), f"{brand.text}/{brand.text}.png")
            # create JSON file "brand.json" with the name of the brand name and img Like this
            # {"name": "brand_name", "img": path_to_img] } import json
            json_data = {
                "name": brand.text,
                "img": f"{brand.text}/{brand.text}.png",
            }
            with open(f"{brand.text}/{brand.text}.json", "w") as f:
                json.dump(json_data, f)
    except EC as e:
        print(e)
    finally:
        driver.close()
        driver.quit()


# collect all models of the brand
def get_models():
    try:
        # open JSON file with all brands
        with open("brands.json", "r") as f:
            brands_url = json.load(f)
        brands = brands_url["brands"]
        for brand in brands:
            driver.get(brand["url"])
            # get all models class name = "car-mini__item"
            # wait while all models will be loaded car-mini__item
            time.sleep(5)

            models = driver.find_elements("class name", "car-mini__item")

            # save all models url in JSON file {"models": ["name": "model_name", "url": "model_url"] }
            models_url = {
                "models": [{"name": '_'.join(model.find_element("class name", "car-mini__name-car").text.split()[0:]),
                            "url": model.find_element("class name", "car-mini__item-content").get_attribute("href")}
                           for
                           model in models]  # list comprehension
            }
            with open(f"{brand['name']}/models.json", "w") as f:
                json.dump(models_url, f)
    except EC as e:
        print(e)
    finally:
        driver.close()
        driver.quit()


def get_model_info(brand):
    with open(f"{brand}/models.json", "r") as f:
        models_url = json.load(f)
    for model in models_url["models"]:
        if not os.path.exists(f"{brand}/{model['name']}"):
            os.mkdir(f"{brand}/{model['name']}")
        # driver.get(model["url"])
        # new = True
        # brand = brand
        # # get current date YYYY-MM-DD
        # date = time.strftime("%Y-%m-%d")
        # car_values = [car_value.text.split()[1] for car_value in driver.find_elements("class name", "car-attr__item")]
        # power = car_values[0]
        # fuel_consumption = car_values[3]
        # max_speed = car_values[2]
        # acceleration = car_values[1]
        # # get all img of the model
        # # main_img = driver.find_element("class name", "car-img__foto").find_element("tag name", "img").get_attribute(
        # #     "src")
        # # urllib.request.urlretrieve(main_img, f"{brand}/{model['name']}/{model['name']}.png")  # download main img
        # price = driver.find_element("class name", "title-box-price__value").text
        # credit_from = driver.find_element("class name", "title-box-payment__value").text
        # # get all img of the model
        # # imgs = driver.find_element("class name", "car-img__color-list").find_elements("class name",
        # #                                                                               "car-img__color-item")
        # # count = 0
        # # for img in imgs:
        # #     img.click()
        # #     time.sleep(3)
        # #     url = driver.find_element("class name", "car-img__foto").find_element("tag name", "img").get_attribute(
        # #         "src")
        # #     urllib.request.urlretrieve(url, f"{brand}/{model['name']}/{model['name']}{model['name']}_{count}.png")
        # #     time.sleep(3)
        # #     count += 1
        # modifications = driver.find_elements("class name", "about-table__box")
        # for modification in modifications:
        #     for mod in modification.find_elements("class name", "about-table__body"):
        #         head = mod.find_element("class name", "about-table__row-inner").find_element("class name",
        #                                                                                      "about-table__name-com")
        #         head.click()
        #         time.sleep(3)
        #         description = driver.find_element("class name", "about-table__description"). \
        #             find_element("class name", "about-table__description-list").find_elements(
        #             "class name", "description-list__item")
        #         for des in description:
        #             des.find_elements("class name", "description-list__title")
        #             title = des.find_element("class name", "description-list__title").text
        #             value = des.find_element("class name", "description-list__inner").find_elements("class name",
        #                                                                                             "description-inner__item")
        #             time.sleep(3)
        #             print(title)
        #             print(value)


def get_car_by_brand(brand: str = None):
    driver.get(f"https://franko-auto.ru/cars/{brand.lower()}/")
    while True:
        try:
            # find element by id use By.ID
            button = driver.find_element(By.ID, "filter--res").find_element(By.CLASS_NAME, "wrapper").find_element(
                By.TAG_NAME, "button")
            # if have not attribute style
            if button.get_attribute("style"):
                break

            button.click()
            time.sleep(10)
        except NoSuchElementException:
            print("Кнопка не найдена на странице")
            time.sleep(3)
            continue
    # collect all urls of the cars special-item__content
    items = driver.find_elements(By.CLASS_NAME, "special-item--v2")
    # json_data cars [{"name": "car_name", "url": "car_url"}]
    json_data = {"cars": [{"name": item.find_element(By.CLASS_NAME, "special-item__name-car").text.split()[1],
                           "url": item.find_element(By.CLASS_NAME, "special-item__content").get_attribute("href")}
                          for item in items]}
    # save json_data in json file brand/cars.json
    with open(f"{brand}/cars.json", "w") as f:
        json.dump(json_data, f)


def collect_url_cars():
    with open("brands.json", "r") as f:
        brands = json.load(f)
    for brand in brands["brands"]:
        get_car_by_brand(brand["name"])


def collect_car_info_json(url: str = None):
    driver.get(url)  # open url
    # get current date YYYY-MM-DD
    result = url.rstrip('/').split('/')[-1]
    brand = driver.find_element(By.CLASS_NAME, "logo").find_element(By.TAG_NAME, "span").text.split()[1]
    model = driver.find_elements(By.CLASS_NAME, "bread__item")[3].text
    date = time.strftime("%Y-%m-%d")
    generation = date
    year = date
    modification = driver.find_elements(By.CLASS_NAME, "content-island__row")[4].find_element(By.CLASS_NAME,
                                                                                              "content-island__value").text
    price = [x for x in driver.find_element(By.CLASS_NAME, "car-info__price-box").find_element(By.CLASS_NAME,
                                                                                               "car-info__price").find_element(
        By.TAG_NAME, "p").text if x.isdigit()]
    price = int(''.join(price))
    credit_from = price // 46  # 46 month
    power = driver.find_elements(By.CLASS_NAME, "mod-info__item")[11].find_element(By.CLASS_NAME,
                                                                                   "mod-info__value").text
    fuel_consumption = driver.find_elements(By.CLASS_NAME, "mod-info__item")[13].find_element(By.CLASS_NAME,
                                                                                              "mod-info__value").text
    max_speed = driver.find_elements(By.CLASS_NAME, "mod-info__item")[16].find_element(By.CLASS_NAME,
                                                                                       "mod-info__value").text
    acceleration = driver.find_elements(By.CLASS_NAME, "mod-info__item")[15].find_element(By.CLASS_NAME,
                                                                                          "mod-info__value").text
    transmission = driver.find_elements(By.CLASS_NAME, "mod-info__item")[8].find_element(By.CLASS_NAME,
                                                                                         "mod-info__value").text
    drive_unit = driver.find_elements(By.CLASS_NAME, "mod-info__item")[10].find_element(By.CLASS_NAME,
                                                                                        "mod-info__value").text
    body_type = "неизвестно"
    volume = driver.find_elements(By.CLASS_NAME, "mod-info__item")[6].find_element(By.CLASS_NAME,
                                                                                   "mod-info__value").text
    engine_type = driver.find_elements(By.CLASS_NAME, "mod-info__item")[20].find_element(By.CLASS_NAME,
                                                                                         "mod-info__value").text
    secure = []
    exterior = []
    interior = []
    comfort = []
    multimedia = []
    for item in driver.find_element(By.CLASS_NAME, "com-info__list").find_elements(By.CLASS_NAME, "com-info__item"):
        if "Безопасность" in item.find_element(By.CLASS_NAME, "com-info__title-mini").text:
            for value in item.find_element(By.CLASS_NAME, "car-info__inner-list").find_elements(By.CLASS_NAME,
                                                                                                "car-info__inner-item"):
                secure.append(value.text)
        elif "Экстерьер" in item.find_element(By.CLASS_NAME, "com-info__title-mini").text:
            for value in item.find_element(By.CLASS_NAME, "car-info__inner-list").find_elements(By.CLASS_NAME,
                                                                                                "car-info__inner-item"):
                exterior.append(value.text)
        elif "Интерьер" in item.find_element(By.CLASS_NAME, "com-info__title-mini").text:
            for value in item.find_element(By.CLASS_NAME, "car-info__inner-list").find_elements(By.CLASS_NAME,
                                                                                                "car-info__inner-item"):
                interior.append(value.text)
        elif "Комфорт" in item.find_element(By.CLASS_NAME, "com-info__title-mini").text:
            for value in item.find_element(By.CLASS_NAME, "car-info__inner-list").find_elements(By.CLASS_NAME,
                                                                                                "car-info__inner-item"):
                comfort.append(value.text)
        elif "Мультимедиа" in item.find_element(By.CLASS_NAME, "com-info__title-mini").text:
            for value in item.find_element(By.CLASS_NAME, "car-info__inner-list").find_elements(By.CLASS_NAME,
                                                                                                "car-info__inner-item"):
                multimedia.append(value.text)
    print(
        brand, model, generation, year, modification, price, credit_from, power, fuel_consumption, max_speed,
        acceleration,
        transmission, drive_unit, body_type, volume, engine_type,
        f"secures {secure}",
        f"exterior {exterior}",
        f"interior {interior}",
        f"comfort {comfort}",
        f"multimedia {multimedia}"
    )

    time.sleep(5)
    images = driver.find_elements(By.CLASS_NAME, "owl-item")
    images = [x.find_element(By.TAG_NAME, "img").get_attribute("src") for x in images if
              x.find_element(By.TAG_NAME, "img").get_attribute("src") != None]
    json_file = {
        "auto": {
            "new": True,
            "id": result,
            "brand": brand,
            "model": model,
            "generation": generation,
            "year": year,
            "modification": modification,
            "price": price,
            "credit_from": credit_from,
            "power": power,
            "fuel_consumption": fuel_consumption,
            "max_speed": max_speed,
            "acceleration": acceleration,
            "transmission": transmission,
            "drive_unit": drive_unit,
            "body_type": body_type,
            "volume": volume,
            "engine_type": engine_type,
            "secure": secure,
            "exterior": exterior,
            "interior": interior,
            "comfort": comfort,
            "multimedia": multimedia,
            "images": []
        }
    }

    count = 0
    for image in images:
        urllib.request.urlretrieve(image,
                                   f"{brand.upper()}/{brand.title()}_{'_'.join(model.split()).title()}/{model.lower()}{credit_from}{result}{count}.jpg")
        json_file["auto"]["images"].append(
            f"{brand.upper()}/{brand.title()}_{model.title()}/{model.lower()}{credit_from}{result}{count}.jpg")
        count += 1

    # create_json file
    count = 0
    with open(
            f"{brand.upper()}/{brand.title()}_{'_'.join(model.split()).title()}/{brand.title()}_{'_'.join(model.split()).title()}{result}.json",
            "w") as file:
        json.dump(json_file, file, indent=4, ensure_ascii=False)


def prepare():
    with open('brands.json', 'r') as file:
        data = json.load(file)
        for brand in data["brands"]:
            try:
                get_model_info(brand["name"])
            except Exception as e:
                print("Ошибка при сборе данных")
                continue
            get_car_by_brand(brand["name"])


def scraping():
    brands = [x for x in os.listdir() if "." not in x]
    for brand in brands:
        with open(f"{brand}/cars.json", "r") as file:
            data = json.load(file)
        for car in data["cars"]:
            try:
                collect_car_info_json(car["url"])
            except Exception as e:
                print("Ошибка при сборе данных")
                continue


# Нужно переименовать папки с марками авто в верхний регистр например KIA

def change_name():
    brands = [x for x in os.listdir() if "." not in x]
    for brand in brands:
        os.rename(brand, brand.upper())


# Нужно переименовать папки с моделями авто в нижний регистр например kia_sorento и убрать пробелы в названии например kia_sorento
def change_model_name():
    brands = [x for x in os.listdir() if "." not in x]
    for brand in brands:
        models = [x for x in os.listdir(brand) if "." not in x]
        for model in models:
            folder_name = translit(model, 'ru', reversed=True).replace(" ", "_").lower()
            os.rename(f"{brand}/{model}", f"{brand}/{folder_name}")


# нужно открыть папку с моделями авто и переименовать файлы в нижний регистр например kia_sorento.json
def change_file_name():
    brands = [x for x in os.listdir() if "." not in x]
    for brand in brands:
        models = [x.title() for x in os.listdir(brand) if "." not in x]
        for model in models:
            files = [x for x in os.listdir(f"{brand}/{model}")]
            for file in files:
                # нужно убрать пробелы в названии файла и переименовать в нижний регистр например kia_sorento.json, kia_sorento0.jpg
                filename = translit(file, 'ru', reversed=True).replace(' ', '_').lower()
                os.rename(f"{brand}/{model}/{file}", f"{brand}/{model}/{filename}")


# пример надо открыть папку с моделями авто там есть json файлы и папки с картинками нужно открыть json файл и в нем поменять название папки с картинками нижний регистр
def change_json():
    brands = [x for x in os.listdir() if "." not in x]
    for brand in brands:
        models = [x for x in os.listdir(brand) if "." not in x]
        for model in models:
            files = [x for x in os.listdir(f"{brand}/{model}")]
            try:
                for file in files:
                    if file.endswith(".json"):
                        with open(f"{brand}/{model}/{file}", "r", encoding="cp1251") as f:
                            data = json.load(f)
                        result = []
                        for image in data["auto"]["images"]:
                            b = brand.upper()
                            m = model.lower()
                            i = image.split("/")[2].replace(" ", "_").lower()
                            path = f"{b}/{m}/{i}"
                            result.append(path)
                        data["auto"]["images"] = []  # очищаем список
                        data["auto"]["images"] = result  # добавляем новый список
                        with open(f"{brand}/{model}/{file}", "w") as f:
                            json.dump(data, f, indent=4, ensure_ascii=False)
            except json.JSONDecodeError:
                continue


if __name__ == '__main__':
    # get_brands()
    # get_models()
    # get_model_info("KIA")
    # prepare()
    # get_car_by_brand("s")
    # collect_url_cars()
    # collect_car_info_json()
    # time.sleep(15)
    # change_json()
    change_name()
    change_model_name()
    change_file_name()
    change_json()

# collect_car_info_json('https://franko-auto.ru/cars/chery/tiggo_4/4146')
# get_car_by_brand()
