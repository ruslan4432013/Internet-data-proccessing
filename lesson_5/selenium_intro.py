import json
import logging
from progress.bar import IncrementalBar
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains


class MailScrubber:
    def __init__(self):
        print('[INFO] Setup drivers')
        self.driver = MailScrubber.setup_driver()
        self.db = MailScrubber.setup_mongo_client()
        self.login()
        self.links_to_mail = set()
        print('[INFO] Drivers installed')
        self.find_all_url_mail()
        self.data_mail_list = []
        self.links = [link for link in self.links_to_mail if isinstance(link, str)]
        self.counter = 1
        list(map(self.parse_page_mail, self.links))

    @staticmethod
    def setup_driver():
        service = Service('./chromedriver.exe')
        chrome_options = Options()
        chrome_options.headless = True
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(15)
        driver.get('https://mail.ru/')
        return driver

    def login(self):
        button_input = self.driver.find_element(By.XPATH, '//button[@data-testid="enter-mail-primary"]')
        button_input.click()
        iframe = self.driver.find_element(By.XPATH, "//iframe[contains(@class, 'iframe')]")
        self.driver.switch_to.frame(iframe)
        input_name = self.driver.find_element(By.XPATH, '//input[@name="username"]')
        input_name.send_keys('study.ai_172@mail.ru')
        input_name.send_keys(Keys.ENTER)
        input_name = self.driver.find_element(By.XPATH, '//input[@name="password"]')
        input_name.send_keys('NextPassword172#')
        input_name.send_keys(Keys.ENTER)
        self.driver.switch_to.default_content()

    def find_all_url_mail(self):
        print('[INFO] Getting urls mail from mail.ru')
        while True:
            current_len = len(list(self.links_to_mail))
            articles = self.driver.find_elements(By.XPATH, "//a[contains(@class, 'llc')]")
            self.links_to_mail.update([article.get_attribute('href') for article in articles])
            actions = ActionChains(self.driver)
            actions.move_to_element(articles[-1])
            actions.perform()
            if len(list(self.links_to_mail)) == current_len:
                break
        print('[INFO] Urls received')

    def parse_page_mail(self, url):
        self.driver.get(url)
        by_whom = self.driver.find_element(By.XPATH,
                                           "//div[@class='letter__author']/span[@class='letter-contact']").text
        letter_date = self.driver.find_element(By.XPATH, "//div[@class='letter__date']").text
        theme_name = self.driver.find_element(By.XPATH, "//h2[@class='thread-subject']").text
        body_mail = self.driver.find_element(By.XPATH, "//div[@class='letter-body']").text
        info_page = {'from': by_whom,
                     'date': letter_date,
                     'theme': theme_name,
                     'body': body_mail}
        self.fill_mongo(info_page)

    def fill_mongo(self, data):
        contains = self.db.mails.find_one({'body': data['body']})

        if not contains:
            self.db.mails.insert_one(data)
            print(f'[INFO] Add mail to MongoDB {self.counter}/{len(self.links) + 1}')
        else:
            print(f'[INFO] Mail is already in MongoDB {self.counter}/{len(self.links) + 1}')
        self.counter += 1

    @staticmethod
    def setup_mongo_client():
        client = MongoClient('localhost', 27017)
        db = client['mails']
        return db


def main():
    mail = MailScrubber()


if __name__ == '__main__':
    main()
