CATEGORIES = {
        "location" : 10,
        "colocation" : 11
        }

REGIONS = {
        "rhone-alpes" : 22
        }

class City:
    """Class to associate a city name with his departement number
    if it's given"""
    def __init__(self, name, code=None):
        self.name = name
        self.code = code

    def __str__(self):
        """Format the output for an url resarch with LBC"""
        if self.code:
            return "{}_{}".format(self.name, self.code)
        else:
            return self.name


class LBCSearchError(Exception):
    """Raise when LBCUrls have some invalid elements during creation"""

class LBCUrls:
    """Function to format an url to perform research on Leboncoin website.
    
    prototype : LBCUrls(region, category, *cities)

    region --> Need an avaible key of REGION
    category --> Key or value of CATEGORIES
    *cities --> list of city to perform research
    """
    WEBSITE = "https://www.leboncoin.fr/"
    def __init__(self, region, category, text=None, *cities):
        #Initialise each attributes
        self.region = None
        self.category = None
        self.cities = []
        self.text = text
        
        self.set_region(region)
        self.set_category(category)
        for city in cities:
            self.add_city(city)

    def set_region(self, region):
        region = region.lower()
        if region not in REGIONS:
            raise LBCSearchError("Invalid region => {}".format(region))
        self.region = REGIONS[region]

    def set_category(self, category):
        """Select a category to perform our research, available element in
        the CATEGORIES dictionnary.
        :arg category --> An int or a str can be passed"""

        category = category.lower()
        #Perform check, if category is an int check dictonnary values,
        #if category is a string check dictionnary keys.
        if (type(category) == int) and category not in CATEGORIES.values():
            raise LBCSearchError("Invalid category => {}".format(category))
        elif (type(category) == str) and category not in CATEGORIES:
            raise LBCSearchError("Invalid category => {}".format(category))
        elif (type(category) != int) and type(category) != str:
            raise TypeError("expected int or str")
        
        #Finally set up our self.category attribute
        if (type(category) == str):
            category = CATEGORIES[category]
        self.category = category


    def add_city(self, city):
        """Add a single city to our cities attribute"""
        if type(city) != City:
            raise LBCSearchError("Expected City object.")
        self.cities.append(city)
    
    def __str__(self):
        url = self.WEBSITE
        url += "recherche/?"

        #add the category
        url += "category={}".format(self.category)

        #add the region
        url += "&regions={}".format(self.region)

        #add research text keyword
        if self.text:
            url += "&text={}".format(self.text)

        #add cities
        number_city = len(self.cities)
        if number_city > 0:
            url += "&location="
        while(number_city > 0):
            city = self.cities.pop()
            url += str(city)
            number_city -= 1
            #Separate each city with a coma
            if number_city != 0:
                url += ','

        return url



if __name__ == "__main__":
    Lyon = City("Lyon", 69009)
    url = LBCUrls("Rhone-Alpes", "location bro", Lyon)
    print(url)
