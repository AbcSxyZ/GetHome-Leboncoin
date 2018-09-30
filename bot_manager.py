#!/usr/bin/python3
# -*- encoding:utf-8  -*-

import os
from LBC_bot import LBCBot
from LaCarteDesCollocs_bot import LCDCBot
from SMTPSender import SMTPSender
from getpass import getpass
from LBC_urls import LBCUrls, City
import subprocess
import time
import sys, re
from smtplib import SMTPAuthenticationError
from Filter import Ad_filter

MAIL = "rossi.sim@outlook.com"
PASS = getpass("{} password : ".format(MAIL))
PORT = 587
HOST = "smtp-mail.outlook.com"

class Bot_Manager:
    """
    Class to manipulate a bot, launching it, send his parsed
    data, manage bot trace
    """
    def __init__(self, url, bot_name, bot_type, bot_working_folder="Bot_data", 
                 bot_filter=Ad_filter(), headless=False, verbose=True):
        #Prepare a Folder for our bot
        self.working_folder = bot_working_folder
        self.name = bot_name
        self.url = url
        self.bot_filter = bot_filter
        self.bot_file = "{}/{}".format(self.working_folder, self.name)
        self.verbose = verbose
        self._prepare_workplace()
        self._login()

        
        x = 1
        while (1):
            self._bprint("Lauching bot. - {}", x)
            self.bot = bot_type(url, self.olds_urls, headless, verbose)

            #Use our filter, ad it the list parsed by the bot and launch the filter
            self.bot_filter.set_list(self.bot.parsed_ads)
            self.bot_filter.launch_filter()

            #Send all of our ad by e-mail
            if len(self.bot_filter.ads) > 0:
                self._send_news(self.bot_filter.ads)

            #Save all new urls in a file to avoid parsing same Ad
            self._update_urls()
            self._bprint("Bot done, start sleeping".format(self.name))
            time.sleep(60)
            x += 1

    def _login(self):
        try:
            self.mail_server = SMTPSender(HOST, MAIL, PASS, PORT)
            self._bprint("Connected to SMTP server.")
        except SMTPAuthenticationError:
            self._bprint("Invalid password for {}.", MAIL)
            sys.exit(1)

    @property
    def website_name(self):
        """Extract the website name from the url, set is as an attribute"""
        host = re.findall("www\..*\.[a-z]{2,3}", self.url)[0]
        site_name = host.split('.')[1]
        return site_name
        

    def _bprint(self, str_format, *args):
        """Function use to print formated message by the bot"""
        if self.verbose == False:
            return None
        to_print = "Bot_manager {} : ".format(self.name)
        to_print += str_format.format(*args)
        print(to_print)

    def _send_news(self, new_ads):
        """Send by mail all new offers"""
        self._login()
        self._bprint("start sending {} mail(s).", len(new_ads))
        for counter, ad in enumerate(new_ads, 1):
            self._bprint("send mail {}/{}", counter, len(new_ads))
            #Prepare the mail subject + receiver 
            mail_subject = self.website_name + " : " + ad.title
            mail = self.mail_server.prepare([MAIL], subject=mail_subject)
            
            #Add the mail body with Ad preformated mail
            self.mail_server.set_content(mail, ad.mail_format(), Type="text")

            #Join all pictures to the mail
            images = self._load_images(ad)
            for img_path in images:
                self.mail_server.add_file(mail, img_path, 
                                filename=img_path)
            self.mail_server.send(mail)


    def _load_images(self, ad):
        """
        Download each jpg files through curl
        return a list of each downloaded files
        """
        downloaded_list = []
        for image in ad.pictures:
            image_id = image.split("/")[-1]
            with open("Bot_data/images/" + image_id, 'wb') as image_file:
                command = subprocess.run(["curl", "-sS", image], stdout=image_file)
                if command.returncode != 0:
                    print("Shell error : {}.".format(command.args))
            downloaded_list.append(image_id)
        return ["Bot_data/images/" + img_path for img_path in downloaded_list]

    def _prepare_workplace(self):
        """
        Check if the bot workplace is set up well,
        Create working folder if needed, retrieve old data if it exists
        """


        #Create a folder for bot's working
        if os.path.exists(self.working_folder) == False:
            os.mkdir(self.working_folder)
            self.olds_urls = None
        #If we don't need to create the folder, check if a file with urls
        #is already existing
        else:
            try:
                with open(self.bot_file, 'r') as bot_parsed_urls:
                    olds_urls = bot_parsed_urls.read().split()
            except:
                olds_urls = None
            self.olds_urls = olds_urls

        #Create our image folder if needed
        if os.path.exists("Bot_data/images") == False:
            os.mkdir("Bot_data/images")

    def _update_urls(self):
        """Save in the bot corresponding file each parsed urls"""
        with open(self.bot_file, 'w') as urls_file:
            new_url_list = self.bot.parsed_urls if self.olds_urls == None \
                                    else self.bot.parsed_urls + self.olds_urls
            for url in new_url_list:
                print(url, file=urls_file)
        self.olds_urls = new_url_list



if __name__ == "__main__":
    big_city = City("Frangy", 74270)
    url = LBCUrls("rhone-alpes", "location", None, big_city)
    LaChambreUrl = "https://www.lacartedescolocs.fr/colocations/auvergne-rhone-alpes/lyon"
    bot_filter = Ad_filter(price_interval=(0, 500), images=True, phone=True)
    Bot_Manager(LaChambreUrl, "LaChambreBot", LCDCBot, headless=True, bot_filter=bot_filter)

