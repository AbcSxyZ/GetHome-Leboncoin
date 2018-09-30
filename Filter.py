#!/usr/bin/python3
# -*- encoding:utf8 -*-

class FilterError(Exception):
    """Raise if filter is set up with wrong elements"""

class Ad_filter:
    """
    True to use an element as a filter
    False do not filter an element
    """
    def __init__(self, ad_set=None, price_interval=(0, 0), images=False, phone=False,
            size=False, rooms=False):
        self.ads = ad_set
        if price_interval[0] > price_interval[1]:
            raise FilterError("Wrong price interval : {} to {}".format(*price_interval))
        self.price = price_interval
        self.images = images
        self.phone = phone
        self.size = size
        self.rooms = rooms

    def set_list(self, ad_list):
        """Use to set a new list to a filter after his initialisation"""
        self.ads = list(ad_list)

    def launch_filter(self):
        """Function to call whenever a set is ready to be cleaned"""
        if self.ads == None:
            raise FilterError("No ads to filter")
        if self.price[0] != 0 or self.price[1] != 0:
            self._keep_desired_price()
        if self.images == True:
            self._remove_empty_pictures()

        remove_list = ["phone"] if self.phone else [None]
        remove_list.append("size" if self.size else None)
        remove_list.append("rooms" if self.rooms else None)
        for attribute in filter(None, remove_list):
            self._remove_empty_element(attribute)



    def _remove_empty_element(self, attribute_name):
        """Remove from the list each ad with a given attribute to None"""
        final_list = []
        for ad in self.ads:
            attribute_value = getattr(ad, attribute_name)
            if attribute_value:
                final_list.append(ad)
        self.ads = final_list

    def _remove_empty_pictures(self):
        """Remove each add without pictures"""
        final_list = []
        for ad in self.ads:
            if len(ad.pictures) != 0:
                final_list.append(ad)
        self.ads = final_list

    def _keep_desired_price(self):
        """
        Keep ads with a price in a specified interval, 
        keep those with no price
        """
        finals_ads = []
        for ad in self.ads:
            if ad.price == None:
                continue
            int_price = atoi(ad.price)
            if self.price[0] <= int_price <= self.price[1]:
                finals_ads.append(ad)
        self.ads = finals_ads

def atoi(string):
    index = 0
    negativ = False
    result = 0
    while index < len(string) and string[index].isspace():
        index += 1
    if index < len(string) and string[index] in ["-", "+"]:
        if string[index] == '-':
            negativ = True
        index += 1
    while index < len(string) and string[index].isdigit():
        result = result * 10 + int(string[index])
        index += 1
    return result * -1 if negativ else result
