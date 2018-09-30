# -*- encoding: utf8 -*-

import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
import imghdr
import re

class SMTPSender:
    """"""
    def __init__(self, Host, User, Pass, Port=465):
        """"Initialize SMTPServer with :
    - Host : smtp host server
    - User : sender's email
    - Pass : sender's password
    attributes:
    - self.email : User email
    - self.Client : SMTP server"""
        #Connect user to his SMTP server
        if Port == 465:
            self.Client = smtplib.SMTP_SSL(Host, Port)
        else:
            self.Client = smtplib.SMTP(Host, Port)
            self.Client.starttls()
        #Log user
        self.Client.login(User, Pass)

        #Save email user
        self.email = User

    def prepare(self, dst, subject=None):
        """Prepare Header when and return message object, From, To and Subject element"""
        msg = EmailMessage()
        msg['From'] = self.email
        msg['To'] = dst
        if subject:
            msg['subject'] = subject
        return msg

    def set_content(self, mail, content, Type='html'):
        """Add the message content,
        available type : html/text"""
        if Type == 'html':
            mail.add_alternative(content, subtype='html')

        elif Type == 'text':
            mail.set_content(content)


    def add_image(self, mail, imagePath, filename='Default'):
        """Add a new image to a pre-made email"""
        with open(imagePath, 'rb') as ImageFile:
            Image = ImageFile.read()
            ImageType = imghdr.what(None, Image)
            mail.add_attachment(Image, maintype='image',
                                subtype=ImageType,
                                filename="{}.{}".format(filename, ImageType))

        return mail

    def add_file(self, mail, filepath, filename='Default'):
        """Add a file as attachment, indicated by his filepath"""
        #Get file extension
        ext = re.findall('.[a-zA-Z]{0,4}$', filepath)[0]

        #Read path and attach it
        with open(filepath, 'rb') as File:
            FileContent = File.read()
            mail.add_attachment(FileContent, maintype='', subtype=ext[1:],
                                filename='{}.{}'.format(filename, ext))


    def add_text(self, mail, text, filename='Default', ext='txt'):
        """Add text as a mail body"""
        mail.add_attachment(text, subtype='plain',
                            filename='{}.{}'.format(filename, ext))

    def send(self, msg):
        """Send message with the smtp client"""
        self.Client.sendmail(msg['From'], msg['To'].split(','), msg.as_string())

