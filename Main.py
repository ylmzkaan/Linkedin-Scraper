# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 23:02:25 2018

@author: kaany
"""

from Classes import LinkedinScraper
from sys import path as syspath
from os import system, path as ospath
from selenium.common.exceptions import WebDriverException

class Main:
    
    def __init__(self):
        
        self.email = None
        self.password = None
        self.keyword = None
        self.personLimit = -1
        self.userInput = None
    
    def main(self):
        
        self._setLoginData()
        self.userInput = self._setUserInput()
        self._handleUserAction()
    
    def _setLoginData(self):
        
        self.email = input("LinkedIn email: ")
        self.password = input("LinkedIn password: ")
        
        print("\nLogin data saved.")
    
    def _setUserInput(self):
    
        self._printMenu()
        
        userInput = input("Select action: ")
        
        if not (userInput == '1' or userInput == '2' or userInput == '3' or userInput == '4'):
            print("\nInvalid input. Try again.\n")
            return self._setUserInput()
            
        return userInput

    def _printMenu(self):
    
        print( """\n\tMENU\n
                Choose action:\n
                1- Search for a keyword and get resultant people's emails\n
                2- Search for a keyword and send invitation to all resultant people\n
                3- Change login username and password\n
                4- Quit""" )
    
    def _handleUserAction(self):
        
        if self.userInput == '1':
            self._scrape()
        elif self.userInput == '2':
            self._sendInvitations()
        elif self.userInput == '3':
            self._setLoginData()
            self.userInput = self._setUserInput()
            self._handleUserAction()
        elif self.userInput == '4':
            print("\nQuitting...")
    
    def _setPersonLimit(self):
                
        personLimit = input("Limit number of people to search for (-1 for infinite): ")
        
        if not self._representsInt(personLimit):
            print("\nYour input must be a number! Try again.\n")
            return self._setPersonLimit()
        
        personLimit = int(personLimit)
        
        if personLimit < -1:
            print("\nYour input must be greater than -1! Try again.\n")
            return self._setPersonLimit()
        
        if personLimit == -1:
            personLimit = 99999
            
        return personLimit
    
    def _scrape(self):
        
        self.keyword = input("Search keyword: ")
        self.personLimit = self._setPersonLimit()
        
        linkedinScraper = LinkedinScraper(self.email, self.password, self.keyword, self.personLimit)
    
        try:
            sessionSuccesful = linkedinScraper.startSession()
            
            if not sessionSuccesful:
                print("Session start failed. Try again.\n")
                linkedinScraper.session.close()
                self.main()
                return
                
            linkedinScraper.scrapePersonData()
        finally:
            
            try:
                linkedinScraper.session.close()
                print("\nGoogle Chrome session is closed.\n")
            except WebDriverException:
                pass
            
    def _sendInvitations(self):
        
        self.keyword = input("Search keyword: ")
        self.personLimit = self._setPersonLimit()
        
        linkedinScraper = LinkedinScraper(self.email, self.password, self.keyword, self.personLimit)
    
        try:
            sessionSuccesful = linkedinScraper.startSession()
            
            if not sessionSuccesful:
                print("Session start failed. Try again.\n")
                linkedinScraper.session.close()
                self.main()
                return
            
            linkedinScraper.sendInvitations()
        finally:
            
            try:
                linkedinScraper.session.close()
                print("\nGoogle Chrome session is closed.\n")
            except WebDriverException:
                pass
    
    def _representsInt(self, s):
        
        try: 
            int(s)
            return True
        except ValueError:
            return False

def mainRoutine():
    
    print("--------\nLinkedIn Profile Scraper\nAll rights reserved\nVERSION: 1.0\n")
    
    try:
        if not _isConnectedToInternet():
            print("\nNO CONNECTION TO INTERNET.\nCONNECT TO INTERNET AND TRY AGAIN.")
            return
            
        mn = Main()
        mn.main()
    except Exception as ex:
        print(ex)
    finally:
        input("Press any key to quit")

def _isConnectedToInternet():
        
    print("\nChecking internet connection...\n")
    return not bool(system("ping google.com > nul"))
    
if __name__ == '__main__':

    chromedriverDir = ospath.join(ospath.dirname(ospath.abspath(__file__)), 'chromedriver.exe')
    if chromedriverDir not in syspath:
        syspath.append(chromedriverDir)
        
    mainRoutine()
    



