#!/usr/bin/python3
# -*- encoding:utf-8 -*-

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from Ad_class import Ad
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import code
import re
import getpass

MAIL = "rossi.sim@outlook.com"
PASS = getpass.getpass(f"Password La carte des colocs for {MAIL} : ")

class LCDCBot:
    WEBSITE = "https://www.lacartedescolocs.fr"
    def __init__(self, url, olds_urls=None, headless=False, verbose=False):
        self._set_browser(headless)
        self._login()
        self.url = url
        self.olds_urls = olds_urls
        self.verbose = verbose

        founded_ads = self._main_urls()
        ads_to_parse = self._remove_olds_urls(founded_ads)
        
        #Parse new founded Ads
        if len(ads_to_parse) > 0:
            self._bprint("Start parsing {} ad(s).", len(ads_to_parse))
        else:
            self._bprint("No ad to parse.")
        parsed_ads = []
        for counter, ad in enumerate(ads_to_parse, 1):
            if self.verbose:
                print("LCDCBot : -- Progess {}/{} --".format(counter, len(ads_to_parse)))
            parsed_ads.append(self._explore_ad(ad))

        self.parsed_ads = parsed_ads

        self.browser.close()

    def _bprint(self, str_format, *args):
        """Function use to print formated message by the bot"""
        if self.verbose == False:
            return None
        to_print = "LCDCBot : " + str_format.format(*args)
        print(to_print)

    @property
    def parsed_urls(self):
        return [ad.link for ad in self.parsed_ads]

    def _set_browser(self, headless):
        optn = Options()
        optn.headless = headless
        self.browser = Firefox(options=optn)
        self.browser.implicitly_wait(30)

    def _login(self):
        self.browser.get(self.WEBSITE + "/users/sign_in")
        self.browser.find_element(By.ID, "user_email").send_keys(MAIL)
        self.browser.find_element(By.ID, "user_password").send_keys(PASS)
        self.browser.find_element(By.CSS_SELECTOR, "button.login_submit_btn").click()
        time.sleep(1)

    
    def _main_urls(self):
        """Retriveve all offers of a research url"""
        self.browser.get(self.url)
        all_ads = self.browser.find_element(By.ID, "listings_container")
        article_list = []

        while len(article_list) == 0:
            article_list = all_ads.find_elements(By.TAG_NAME, "article")

        #Go through each article tag to retrive the offer url, title,
        #and publication date
        Ad_list = []
        for article in article_list:
            url_id = article.get_attribute("data-url-token")
            full_url = self.url + "/a/" + url_id
            ad_name = article.find_element(By.CSS_SELECTOR, "a.info_title").text
            date = article.find_element(By.CSS_SELECTOR, "div.thumb_footer").text
            #Create a new Ad instance from founded information
            new_ad = Ad(ad_name, full_url, publication_date=date.strip())
            Ad_list.append(new_ad)
        return Ad_list

    def _remove_olds_urls(self, ad_list):
        if self.olds_urls == None:
            return ad_list
        finals_ads = []
        for ad in ad_list:
            if ad.link not in self.olds_urls:
                finals_ads.append(ad)
        return finals_ads



    def _explore_ad(self, ad):
        """Get all information from a selected ap"""
        self.browser.get(ad.link)
        #Wait Ajax call
        time.sleep(1.3)
        offer = self.browser.find_element(By.CSS_SELECTOR, "article.big_listing_for_ads")
        self._current_ad = offer
        
        #Get the description, proprietary name, price and address of an add
        #Each of this attribute just will be found based on a css selector
        TAGS_CSS = {
                "description" : "div.listing_message_container.ng-binding",
                "price" : "div.listing_cost_wrapper div.listing_rent",
                "address" : "div.listing_address",
                }
        for attribute, css_selector in TAGS_CSS.items():
            text = self._find_attribute_text(css_selector)
            exec("ad.set_{}(text)".format(attribute))
        
        #Add phone number, proprietary and images attributes with specifics rules
        ad.set_proprietary(self._get_proprietary())
        phone_number = self._get_phone()
        ad.set_phone(phone_number)
        images_urls = self._get_images_urls()
        for image in images_urls:
            ad.set_picture(image)
        return ad
    
    def _get_proprietary(self):
        name_lists = self._current_ad.find_elements(By.CSS_SELECTOR,
                "span.listing_name")
        for name_tab in name_lists:
            if name_tab.is_displayed():
                return name_tab.text

    def _get_images_urls(self):
        """Get all images of the current working add"""
        carousel = self._current_ad.find_element(By.CSS_SELECTOR, "ul.listing_carousel")
        source_code = carousel.get_attribute("innerHTML")
        urls = re.findall(
                "https://lcdcfrance-prod.s3.amazonaws.com/pictures/.*\.jpg",
                source_code)
        return urls

    def _get_phone(self):
        """Find the phone number of the current searched Ad"""
        wrapper = self._current_ad.find_element(By.CSS_SELECTOR, "div.buttons_wrapper")
        button = wrapper.find_elements(By.CSS_SELECTOR, "div.listing_footer_btn")[0]
        try:
            button.click()
        except ElementNotInteractableException:
            return "Agency"
        number = button.find_element(By.CSS_SELECTOR, "span.phone_number").text
        return number

    def _find_attribute_text(self, css_selection):
        """Return the text of a given research with a css selector"""
        try:
            tag = self._current_ad.find_element(By.CSS_SELECTOR, css_selection)
            return tag.text
        except NoSuchElementException as e:
            raise e



if __name__ == "__main__":
    pass
