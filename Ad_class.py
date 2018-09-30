class Ad:
    """Object to represent an Ad of Leboncoin website,
    mainly for renting ads"""
    def __init__(self, title, link, price=None, pictures=None, phone=None, 
                description=None, proprietary=None, size=None, rooms=None,
                publication_date=None, address=None):
        self.title = title
        self.link = link
        self.set_price(price)
        self.set_phone(phone)
        self.set_description(description)
        self.set_proprietary(proprietary)
        self.set_size(size)
        self.set_rooms(rooms)
        self.set_publication_date(publication_date)
        self.set_address(address)

        #Need a list or None for pictures. Loop over each image to save it
        self.pictures = []
        if pictures and type(pictures) == list:
            for pic in pictures:
                self.set_picture(pic)
        elif pictures != None:
            raise TypeError("Invalid type for pictures : {}.".format(pictures))

    def __repr__(self):
        Ad_repr = "Ad name : {}\nAd link : {}\n".format(self.title, self.link)
        Ad_repr += "Proprietary : {} | ".format(self.proprietary)
        if self.phone:
            Ad_repr += "phone number : {} | ".format(self.phone)
        Ad_repr += "Publication : {}".format(self.publication_date)
        Ad_repr += "\n"
        if self.price:
            Ad_repr += "Price : {}\n".format(self.price)
        if self.size:
            Ad_repr += "Size : {}\n".format(self.size)
        if self.rooms:
            Ad_repr += "Rooms : {}\n".format(self.rooms)
        Ad_repr += "\nDESCRIPTION : \n{}\n".format(self.description)
        if len(self.pictures) > 0:
            Ad_repr += "\nImages:\n"
            for image in self.pictures:
                Ad_repr += "{}\n".format(image)
        return Ad_repr

    def mail_format(self):
        """
        Format an ad to be send by email, create the body of the mail with
        available informations
        """
        #Add mail header with proprietary informations
        mail_str = ""
        mail_str += self.proprietary
        if self.phone:
            mail_str += " | " + self.phone
        mail_str += " | " + self.publication_date + "\n"
        mail_str += self.link + "\n\n"

        if self.address:
            mail_str += self.address + "\n"
        #Add optional element to our mail string
        price_str = "Price : {}".format(self.price) if self.price else None
        rooms_str = "Rooms : {}".format(self.rooms) if self.rooms else None
        size_str = "Size : {}".format(self.size) if self.size else None
        extra = [price_str, rooms_str, size_str]
        extra = list(filter(None, extra))
        #Loop over each formated string to add it
        for index, option_str in enumerate(extra):
            mail_str += option_str
            if index + 1 != len(extra):
                mail_str += ' | '
        if len(extra) >= 1:
            mail_str += '\n\n'

        #Add the description
        mail_str += "\nDESCRIPTION : \n" + self.description + "\n"
        return mail_str



    def set_publication_date(self, publication_date):
        self.publication_date = publication_date

    def set_rooms(self, rooms):
        self.rooms = rooms

    def set_size(self, size):
        self.size = size

    def set_price(self, price):
        self.price = price

    def set_picture(self, picture):
        self.pictures.append(picture)

    def set_phone(self, phone):
        self.phone = phone

    def set_proprietary(self, proprietary):
        self.proprietary = proprietary

    def set_description(self, description):
        self.description = description

    def set_address(self, address):
        self.address = address

