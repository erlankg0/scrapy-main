import datetime
import json
import os
import time
import urllib.request
import random
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from transliterate import translit
from urllib.error import URLError


class Driver:
    def __init__(self, url):
        self.options = webdriver.ChromeOptions()
        self.service = Service(
            'C:\\Users\\User\\PycharmProjects\\scapingnew\\driver\\chromedriver.exe')  # path to chromedriver.exe

        self.ua = UserAgent()
        self.userAgent = self.ua.random
        self.options.add_argument(f'user-agent={self.userAgent}')
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--disable-notifications")
        self.options.add_argument("--disable-infobars")

        self.driver = webdriver.Chrome(
            service=self.service,
            options=self.options,
            executable_path='C:\\Users\\User\\PycharmProjects\\scapingnew\\driver\\chromedriver.exe'
        )
        self.url = url

    def get_brands(self):
        self.driver.get(self.url)  # open url
        # get all brands class name = "mark__item"
        try:
            brands = self.driver.find_elements(By.CLASS_NAME, "mark__item")
            # save all brands url in JSON file
            brands_url = {
                "brands": [
                    {
                        "name": brand.text,
                        "url": brand.find_element("class name", "mark__link").get_attribute("href")
                    }
                    for brand in brands
                ]  # list comprehension
            }
            # write JSON file
            with open("brands.json", "w", encoding="utf-8") as file:
                json.dump(brands_url, file, indent=4, ensure_ascii=False)
            for brand in brands:
                # create folder for each brand
                if not os.path.exists(brand.text.upper()):
                    os.mkdir(brand.text.upper())
                # download image for each brand
                wait = WebDriverWait(self.driver, 10)
                img = brand.find_element(By.CLASS_NAME, "lazy")
                urllib.request.urlretrieve(img.get_attribute("src"), f"{brand.text.upper()}/{brand.text.upper()}.jpg")
                json_data = {
                    "name": brand.text,
                    "image": f"{brand.text.upper()}/{brand.text.upper()}.png",
                }
                # write JSON file
                with open(f"{brand.text.upper()}/{brand.text.upper()}.json", "w", encoding="utf-8") as file:
                    json.dump(json_data, file, indent=4, ensure_ascii=False)
        except EC as e:
            print(f"Ошибка: {e}")
        finally:
            self.driver.quit()
            self.driver.close()

    # collect all models for each brand
    def get_models(self):
        try:
            # open JSON file with brands
            with open("brands.json", "r", encoding="utf-8") as file:
                brands = json.load(file)
            for brand in brands["brands"]:
                self.driver.get(brand["url"])
                # get list of models
                models = self.driver.find_element(
                    By.CLASS_NAME,
                    "car-mini__grid"
                ).find_elements(
                    By.CLASS_NAME,
                    "car-mini__item"
                )
                models_url = {
                    "models": [
                        {"name": translit(
                            '_'.join(model.find_element("class name", "car-mini__name-car").text.split()[0:]), 'ru',
                            reversed=True).replace(" ", "_").lower(),
                         "url": model.find_element("class name", "car-mini__item-content").get_attribute("href")
                         }
                        for model in models
                    ]  # list comprehension
                }

                with open(f"{brand['name'].upper()}/models.json", "w", encoding="utf-8") as file:
                    json.dump(models_url, file, indent=4, ensure_ascii=False)

        except EC as e:
            print(f"Ошибка: {e}")
        finally:
            self.driver.quit()
            self.driver.close()

    def create_folder_models(self):
        brands = [x for x in os.listdir() if '.' not in x]
        for brand in brands:
            with open(f"{brand}/models.json", "r", encoding="utf-8") as file:
                models = json.load(file)
            for model in models["models"]:
                # create folder for each model
                model = model["name"].lower()
                model = translit(model, 'ru', reversed=True).replace(" ", "_").lower()
                if not os.path.exists(f"{brand}/{model}"):
                    os.mkdir(f"{brand}/{model}")
                    print(f"Создана папка {brand}/{model}")

    def collect_auto_by_models(self):
        brands = [x for x in os.listdir() if '.' not in x]

        for brand in brands:
            with open(f"{brand}/models.json", "r", encoding="utf-8") as file:
                models = json.load(file)

            try:
                for model in models["models"]:

                    self.driver.get(model["url"])
                    # list color name
                    header = self.driver.find_element(By.TAG_NAME, 'header')
                    self.driver.execute_script('arguments[0].style.position = "relative";', header)

                    colors = self.driver.find_element(
                        By.CLASS_NAME, 'car-img__color-list'
                    ).find_elements(
                        By.CLASS_NAME, 'car-img__color-item'
                    )
                    # randon color
                    color = random.choice(colors)
                    color.click()
                    if not os.path.exists(f"{brand}/{model['name'].lower()}"):
                        os.mkdir(f"{brand}/{model['name'].lower()}")
                    # get image
                    img = self.driver.find_element(By.CLASS_NAME, "car-img__foto").find_element(By.TAG_NAME, "img")
                    urllib.request.urlretrieve(
                        img.get_attribute("src"),  # get image url
                        f"{brand}/{model['name'].lower()}/{model['name'].lower()}.jpg"  # save image
                    )
                    brand_name = self.driver.find_element(By.CLASS_NAME, "bread__box").find_elements(By.TAG_NAME, "li")[
                        2].text
                    model_name = self.driver.find_element(By.CLASS_NAME, "bread__box").find_elements(By.TAG_NAME, "li")[
                        3].text
                    print(f"Марка: {brand_name}, Модель: {model_name}")
                    modifications = self.driver.find_elements(By.CLASS_NAME, "about-table__box")
                    length = 0
                    for modification in modifications:
                        engine = modification.text.split()[0] + " " + modification.text.split()[1]
                        print(f"Двигатель: {engine} {length} ")
                        bodies = modification.find_elements(By.CLASS_NAME, "about-table__body")

                        # get price
                        price = \
                            modification.find_element(By.CLASS_NAME, "about-table__body").find_element(By.CLASS_NAME,
                                                                                                       "about-table__row-inner").find_elements(
                                By.CLASS_NAME, "about-table__cell")[3].get_attribute("data-num")
                        credit_from = int(price) // 53
                        print(f"Цена: {price} Кредит от: {credit_from} рублей в месяц")

                        for body in bodies:
                            mod_name = body.find_element(By.CLASS_NAME, 'about-table__name-com').text
                            mod_name = translit(mod_name, 'ru', reversed=True).replace(" ", "_").lower()
                            body.find_element(By.CLASS_NAME, 'about-table__name-com').click()
                            time.sleep(1)

                            print(f"Модификация: {mod_name} Цена: {price}")
                            # get current block class name "about-table__description"
                            block = self.driver.find_element(By.CLASS_NAME, "about-table__description")
                            # get ul list
                            ul = block.find_element(By.CLASS_NAME, "about-table__description-list")
                            # get li list
                            li = ul.find_elements(By.CLASS_NAME, "description-list__item")
                            # get all li text
                            secure = []
                            exterior = []
                            interior = []
                            comfort = []
                            multimedia = []
                            other = []
                            for i in li:
                                if i.find_element(By.CLASS_NAME, "description-list__title").text == "Безопасность":
                                    items = i.find_element(By.CLASS_NAME, "description-list__inner").find_elements(
                                        By.TAG_NAME, "li")
                                    for item in items:
                                        secure.append(item.text)
                                    print(f"Безопасность: {secure}")
                                elif i.find_element(By.CLASS_NAME, "description-list__title").text == "Экстерьер":
                                    items = i.find_element(By.CLASS_NAME, "description-list__inner").find_elements(
                                        By.TAG_NAME, "li")
                                    for item in items:
                                        exterior.append(item.text)
                                    print(f"Экстерьер: {exterior}")
                                elif i.find_element(By.CLASS_NAME, "description-list__title").text == "Интерьер":
                                    items = i.find_element(By.CLASS_NAME, "description-list__inner").find_elements(
                                        By.TAG_NAME, "li")
                                    for item in items:
                                        interior.append(item.text)
                                    print(f"Интерьер: {interior}")
                                elif i.find_element(By.CLASS_NAME, "description-list__title").text == "Комфорт":
                                    items = i.find_element(By.CLASS_NAME, "description-list__inner").find_elements(
                                        By.TAG_NAME, "li")
                                    for item in items:
                                        comfort.append(item.text)
                                    print(f"Комфорт: {comfort}")
                                elif i.find_element(By.CLASS_NAME, "description-list__title").text == "Мультимедиа":
                                    items = i.find_element(By.CLASS_NAME, "description-list__inner").find_elements(
                                        By.TAG_NAME, "li")
                                    for item in items:
                                        multimedia.append(item.text)
                                    print(f"Мультимедиа: {multimedia}")
                                else:
                                    items = i.find_element(By.CLASS_NAME, "description-list__inner").find_elements(
                                        By.TAG_NAME, "li")
                                    for item in items:
                                        other.append(item.text)
                                    print(f"Другое: {other}")
                            # save data to json file
                            self.driver.find_elements(By.CLASS_NAME, "about-menu__item")[1].click()
                            power = \
                                self.driver.find_elements(By.CLASS_NAME, "specifications-table__body")[11].find_element(
                                    By.CLASS_NAME, "specifications-table__value").find_elements(
                                    By.CLASS_NAME, "specifications-table__cell")[length].text
                            volume = \
                                self.driver.find_elements(By.CLASS_NAME, "specifications-table__body")[6].find_element(
                                    By.CLASS_NAME, "specifications-table__value").find_elements(
                                    By.CLASS_NAME, "specifications-table__cell")[length].text
                            fuel_consumption = \
                                self.driver.find_elements(By.CLASS_NAME, "specifications-table__body")[13].find_element(
                                    By.CLASS_NAME, "specifications-table__value").find_elements(
                                    By.CLASS_NAME, "specifications-table__cell")[length].text
                            max_speed = \
                                self.driver.find_elements(By.CLASS_NAME, "specifications-table__body")[16].find_element(
                                    By.CLASS_NAME, "specifications-table__value").find_elements(
                                    By.CLASS_NAME, "specifications-table__cell")[length].text
                            acceleration = \
                                self.driver.find_elements(By.CLASS_NAME, "specifications-table__body")[15].find_element(
                                    By.CLASS_NAME, "specifications-table__value").find_elements(
                                    By.CLASS_NAME, "specifications-table__cell")[length].text
                            transmission = \
                                self.driver.find_elements(By.CLASS_NAME, "specifications-table__body")[8].find_element(
                                    By.CLASS_NAME, "specifications-table__value").find_elements(
                                    By.CLASS_NAME, "specifications-table__cell")[length].text
                            drive_unit = \
                                self.driver.find_elements(By.CLASS_NAME, "specifications-table__body")[10].find_element(
                                    By.CLASS_NAME, "specifications-table__value").find_elements(
                                    By.CLASS_NAME, "specifications-table__cell")[length].text
                            engine_type = \
                                self.driver.find_elements(By.CLASS_NAME, "specifications-table__body")[20].find_element(
                                    By.CLASS_NAME, "specifications-table__value").find_elements(
                                    By.CLASS_NAME, "specifications-table__cell")[length].text
                            print(f"Мощность: {length} {power}")
                            print(f"Объем: {length} {volume}")
                            print(f"Расход топлива: {length} {fuel_consumption}")
                            print(f"Максимальная скорость: {length} {max_speed}")
                            print(f"Разгон до 100 км/ч: {length} {acceleration}")
                            print(f"Коробка передач: {length} {transmission}")
                            print(f"Привод: {length} {drive_unit}")
                            print(f"Тип двигателя: {length} {engine_type}")

                            print("Сохраняем данные в json файл")
                            data = {
                                "auto": {
                                    "new": True,
                                    "brand": brand_name,
                                    "model": model_name,
                                    "modification": mod_name,
                                    "generation": datetime.datetime.now().strftime("%Y-%m-%d"),
                                    "engine": engine,
                                    "year": datetime.datetime.now().strftime("%Y-%m-%d"),
                                    "price": price,
                                    "credit_from": credit_from,
                                    "power": power,
                                    "volume": volume,
                                    "fuel_consumption": fuel_consumption,
                                    "max_speed": max_speed,
                                    "acceleration": acceleration,
                                    "transmission": transmission,
                                    "drive_unit": drive_unit,
                                    "engine_type": engine_type,
                                    "body_type": "неизвестно",
                                    "secure": secure,
                                    "exterior": exterior,
                                    "interior": interior,
                                    "comfort": comfort,
                                    "multimedia": multimedia,
                                    "other": other,
                                    "image": [f"{brand}/{model['name'].lower()}/{model['name'].lower()}.jpg"]
                                }
                            }
                            # create folder for modifications
                            if not os.path.exists(f"{brand}/{model['name'].lower()}/{mod_name.lower()}"):
                                os.mkdir(f"{brand}/{model['name'].lower()}/{mod_name.lower()}")
                            # save data to json file utf-8
                            with open(
                                    f"{brand}/{model['name'].lower()}/{mod_name.lower()}/{mod_name.lower()}{length}.json",
                                    "w", encoding="utf-8") as f:
                                json.dump(data, f, ensure_ascii=False, indent=4)

                            self.driver.find_elements(By.CLASS_NAME, "about-menu__item")[0].click()
                            time.sleep(1)
                            # save data to json file utf-8
                        length += 1
            except URLError as e:
                print(f"URLError error : {e.reason}")


if __name__ == '__main__':
    url = "https://franko-auto.ru/cars/"
    driver = Driver(url)
    # driver.get_brands()
    # driver.get_models()
    # driver.create_folder_models()
    driver.collect_auto_by_models()
