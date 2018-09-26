class Cookie:
    def __init__(self, CookieStrings):
        self._CookieStrings = CookieStrings

        code =  self._CookieStrings[0].split('=')
        self.code = {code[0]: code[1]}

        self.info = {"EXTRA": []}
        for param in self._CookieStrings[1:]:
            if '=' in param:
                param, value = param.split('=')
                self.info[param] = value

            else:
                self.info['EXTRA'] += [param]




class HttpResponse:
    """Class use to manipulate an HTTP response in a string format and return
    a formated dictionnary to get all information

    exemple :
    HTTP/1.1 200 OK
    Server: ServerTest
    Date: Wed, 11 May 2017 14:23:17 GMT
    Content-Type: text/html; charset=UTF-8
    Transfer-Encoding: chunked
    Connection: keep-alive
    ...

    >>>Object = HttpResponse(ResponseText)
    >>>Object.data  #{'Server': ['ServerTest'],
                    #'Date':[' Wed, 11 May 2017 14:23:17 GMT'],
                    #'Content-Type' : ['text/html', 'charset=UTF-8'], ...}
    """

    def __init__(self, Response):
        """Available attributs:
        - self.strResponse  --> Http response as String
        - self.status       --> Request status
        - self.data         --> Get all formated data"""
        self.strResponse = Response.replace('\r', '')
        self._cleanResponse()
        self._CookiesSetUp()

    def _cleanResponse(self):
        ResponseList = [line for line in self.strResponse.split('\n') if line != '']

        #Define response status
        self.status = ResponseList[0]

        #Loop over each line to split line with format like :
        #paramater1: value1[; value2]
        #paramater2: value1[; value2]
        self.data = {}
        for ResponseLine in ResponseList[1:]:
            attrName, value = ResponseLine.split(':', maxsplit=1)


            #Check if there is mutliple line for a same parameter name (ex:Cookies)
            if self.data.get(attrName):
                FirstParam = self.data[attrName]
                #In case where it's params 2nd line
                if type(FirstParam[0]) == str:
                    self.data[attrName] = [FirstParam, self._Strip_str(value.split(';'))]
                #In case where params is here 3 times or more, having already list
                else:
                    self.data[attrName].append(self._Strip_str(value.split(';')))

            #If it's a new argument
            else:
                self.data[attrName] = self._Strip_str(value.split(';'))

    def _Strip_str(self, UnstripList):
        """Strip all strings in a list"""
        return [args.strip() for args in UnstripList]


    def _CookiesSetUp(self):
        self.CookiesList = []
        for x, cookieBrut in enumerate(self.data['Set-Cookie']):
            cookie = Cookie(cookieBrut)
            self.CookiesList.append(cookie)

    def UseCookie(self):
        """Format string to reuse cookies for a client"""
        response = 'Cookie: '
        for cookie in self.CookiesList:
            key = list(cookie.code.keys())[0]
            value = list(cookie.code.values())[0]
            response += '{}={}; '.format(key, value)

        return response[:-2]





def main():
    pass




if __name__ == '__main__':
    main()
