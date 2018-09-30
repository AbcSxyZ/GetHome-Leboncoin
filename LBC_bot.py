#!/usr/bin/python3

from LBC_urls import LBCUrls, City
from selenium.webdriver.common.by import By
from selenium.webdriver import FirefoxProfile
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from Ad_class import Ad
from utils import *
import time
import re
import sys
import code

class LBCBot:
    """Bot use to parse each ad of a given url, save each data in Ad object"""
    def __init__(self, url, old_urls=None, headless=False, verbose=False):
        """
        Arguments : 
        url -> Leboncoin valid research url
        old_data -> already parsed set of urls

        Attributes :
        url -> url of a research
        old_urls -> set of old urls already parsed by the bot
        parsed_ads -> List of Ad object parsed for the current session
        """
        #Set up the bot browser
        self._set_browser(headless)
        #Fix class attributes
        self.url = url
        self.old_urls = old_urls
        self.verbose = verbose

        #Make a resarch on the first url to get Ads_to_parse attribute
        self._get_main_url()

        parsed_ads = []
        if self.verbose:
            print("Start parsing {} ad(s) with a bot.".format(len(self.Ads_to_parse)))
        for x, ad in enumerate(self.Ads_to_parse):
            if self.verbose:
                print("Ads progression : {}/{}".format(x + 1, len(self.Ads_to_parse)))
            parsed_ads.append(self._explore_ad(ad))
            time.sleep(5)
        self.parsed_ads = parsed_ads

        self.browser.close()
    
    @property
    def parsed_urls(self):
        """Return all urls parsed by the bot current session"""
        return [ad.link for ad in self.parsed_ads]

    def _set_browser(self, headless=True):
        """Set up a bot browser with desired options"""
        #Set headless browser flag
        optn = Options()
        optn.headless = headless

        #Browser creation
        self.browser = Firefox(options=optn)

    def _get_main_url(self):
        """
        Make a get request on the url research we have to parse
        Get all urls in the webpage, remove already parsed to finally
        set up Ads_to_parse attribute.
        """
        self.browser.get(self.url)
        #Remove cookie window
        try:
            alert = self.browser.find_element(By.CSS_SELECTOR,
                    "button[title=\"J'ai compris\"]")
            alert.click()
        except:
            pass
        potential_urls = self._parse_urls()
        self.Ads_to_parse = self._remove_old_urls(potential_urls)

    def _parse_urls(self):
        """Get all offer urls of a Leboncoin research"""
        #Each offer block represented with the followed css selector
        elems = self.browser.find_elements(By.CSS_SELECTOR, 
                "li[itemtype='http://schema.org/Offer']")
        
        #Go through each block catchink the single "a" tag
        #Ad_list will be a list of Ad object
        Ad_list = []
        for offer in elems:
            link = offer.find_element(By.CSS_SELECTOR, "a")
            url = link.get_attribute("href")
            title = link.get_attribute("title")
            Ad_list.append(Ad(title, url))
        
        #Remove already parsed if needed with _remove_old_urls()
        return Ad_list

    def _remove_old_urls(self, ad_list):
        """Compare some new found urls with an old set of urls given
        to the bot"""
        #If no old set is available
        if self.old_urls == None:
            return ad_list
        #Return a final list of add who need to be parsed
        final_ads = []
        for ad in ad_list:
            if ad.link not in self.old_urls:
                final_ads.append(ad)
        return final_ads

    def _explore_ad(self, ad):
        """
        Function to open a new ad of Leboncoin, and parse desired item
        Searched element in an ad : 
            - proprietary
            - size un square meter
            - description
            - phone numer
            - number of rooms
            - images
            - price
            - publication date
        """
        #Load the page
        self.browser.get(ad.link)

        #Get all images
        images_list = self._get_images()
        for image in images_list:
            ad.set_picture(image)
        
        #Call for functions for each desired items
        #Get mandatory (obligatory) elements
        ad.set_proprietary(self._get_proprietary())
        ad.set_publication_date(self._get_publication_date())
        ad.set_description(self._get_description())

        #Get optionnal elements
        ad.set_price(self._get_price())
        ad.set_rooms(self._get_rooms())
        ad.set_size(self._get_size())
        ad.set_phone(self._get_phone())
        return ad

    def _get_publication_date(self):
        """Search a publication date"""
        publication_tag = self.browser.find_element(By.CSS_SELECTOR,
                "div[data-qa-id='adview_date']")
        return publication_tag.text

    def _get_images(self):
        """
        Get all image's link of an add with a .jpg extension
        available on the img[0-9].leboncoin.fr host
        """
        #Get in first all the page source code
        source_code = self.browser.page_source

        #Catch all links
        images_list = re.findall(
                "https://img[0-9]\.leboncoin\.fr/ad-image/[0-9a-zA-Z]*\.jpg",
                source_code)
        return set(images_list)

    def _get_price(self):
        """Try to catch a price if it exists"""
        try:
            price_tag = self.browser.find_element(By.CSS_SELECTOR, 
                "div[data-qa-id='adview_price'] span._1F5u3")
        except NoSuchElementException:
            return None

        #Remove kind of "<!-- react-text: -->" elements
        span_text = price_tag.get_attribute("innerHTML")
        price = re.sub("<[ /!a-z:0-9-]{0,}>", "", span_text)
        return price
    
    def _get_rooms(self):
        """Search the number of rooms for the rent if availble"""
        try:
            rooms_tag = self.browser.find_element(By.CSS_SELECTOR,
                    "div[data-qa-id='criteria_item_rooms'] div._3Jxf3")
            return rooms_tag.text
        except NoSuchElementException:
            return None

    def _get_size(self):
        """Search the size in square meter"""
        try:
            size = self.browser.find_element(By.CSS_SELECTOR, \
                    "div[data-qa-id='criteria_item_square'] div._3Jxf3")
        except:
            return None
        square_size = re.findall("[0-9]{1,3} m²", size.text)
        return square_size[0]

    def _get_proprietary(self):
        """Search the proprietary name of an ad"""
        try:
            owner_tag = self.browser.find_element(By.CSS_SELECTOR, "div._2rGU1")
        except NoSuchElementException:
            owner_tag = self.browser.find_element(By.CSS_SELECTOR, 
                    "span[data-qa-id=\"storebox_title\"]")
        return owner_tag.text

    def _get_description(self):
        """Get the entire description of an add"""
        desc_tag = self.browser.find_element(By.CSS_SELECTOR, \
                        "div[data-qa-id='adview_description_container']")
        #Check if is full description is available or splitted 
        #with a read more. Extend it if needed
        try:
            read_more = desc_tag.find_element(By.CSS_SELECTOR, \
                            "span._3UcVd")
            read_more.click()
        except NoSuchElementException:
            pass
        return desc_tag.text

    def _get_phone(self):
        """Search a phone number in an ad"""
        #First, check if the phone button exists
        try:
            phone_button = self.browser.find_element(By.CSS_SELECTOR,
                        "div[data-qa-id='adview_button_phone_contact']")
        except NoSuchElementException:
            return None
        #Click on in if exist and extract data in href tag
        phone_button.click()
        time.sleep(0.3)
        try:
            phone_link = phone_button.find_element(By.TAG_NAME, "a")
        except:
            return "phone locked..."
        number = phone_link.get_attribute("href")
        number = number.replace("tel:","")
        return number
