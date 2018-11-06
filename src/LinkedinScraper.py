# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 00:33:19 2018

@author: kaany
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from ProfileScraper import ProfileScraper
from InvitationSender import InvitationSender
import csv
from datetime import datetime
from time import sleep
import locale
import xlsxwriter

class LinkedinScraper:

    def __init__(self, email, password, searchKeyword, personLimit):
        self.email = email
        self.password = password
        self.searchKeyword = searchKeyword
        self.personLimit = personLimit - 1
        self.numberOfProfilesScraped = 0
        self.session = None

    def startSession(self):
        caps = DesiredCapabilities.CHROME
        caps['loggingPrefs'] = {'performance': 'ALL'}

        self.session = webdriver.Chrome(desired_capabilities=caps)
        self.session.implicitly_wait(5)

        HOMEPAGE_URL = 'https://www.linkedin.com'

        self.session.get(HOMEPAGE_URL)

        responseOk = self._checkResponseStatus()
        if not responseOk:
            return False

        emailElement = self.session.find_element_by_id('login-email')
        passwordElement = self.session.find_element_by_id('login-password')

        emailElement.send_keys(self.email)
        passwordElement.send_keys(self.password)

        loginButton = self.session.find_element_by_id('login-submit')
        loginButton.click()

        if not self._isLoginSuccesful():
            print('Login failed. Error in email or password.')
            return False

        print("Login succesful")
        return True

    def _isLoginSuccesful(self):
        if 'There were one or more errors in your submission.' in self.session.page_source:
            return False
        return True

    def scrapePersonData(self):
        scraper = ProfileScraper(self)
        profileLinks = scraper.scrapeAllProfileLinks()

        if profileLinks == []:
            print("NO PROFILE FOUND.")
            return

        data = scraper._extractInfoFromProfileLinks(profileLinks)
        self._saveToCSV(data)

    def sendInvitations(self):
        IS = InvitationSender(self)
        IS.sendInvitationToAll()

    def _saveToCSV(self, data):

        workbook = xlsxwriter.Workbook("LinkedIn " + self.searchKeyword + ".xlsx")
        worksheet = workbook.add_worksheet()

        worksheet.write(0, 0, 'Search Date')
        worksheet.write(0, 1, 'Keyword')
        worksheet.write(0, 2, 'Number of Results')
        worksheet.write(1, 0, datetime.today().strftime('%d-%m-%Y'))
        worksheet.write(1, 1, self.searchKeyword)
        worksheet.write(1, 2, len(data))

        worksheet.write(3, 0, 'Name')
        worksheet.write(3, 1, 'Email')
        worksheet.write(3, 2, 'LinkedIn Profile Link')

        row = 4

        for itemRow in data:
            col = 0
            for item in itemRow:
                worksheet.write(row, col, item)
                col += 1
            row += 1

        print("Data has been saved to file: LinkedIn " + self.searchKeyword + ".xlsx")

        workbook.close()

    def _loadAllSearchResults(self):
        sleep(1)
        #Scroll down enough to let other results to be rendered
        self.session.execute_script("window.scrollTo(0, window.scrollY + 600);")
        sleep(1)
        #Scroll down enough to let other results to be rendered
        self.session.execute_script("window.scrollTo(0, window.scrollY + 600);")
        sleep(1)
        #Scroll down enough to let other results to be rendered
        self.session.execute_script("window.scrollTo(0, window.scrollY + 600);")

    def _isNameLinkedInMember(self, profileItem):
        name = profileItem.find_element_by_css_selector("span.actor-name").text
        if name == 'LinkedIn Member':
            return True
        return False

    def _searchForKeyword(self):
        searchFormDiv = self.session.find_element_by_class_name('nav-search-bar')
        searchForm = searchFormDiv.find_element_by_tag_name('input')

        searchForm.send_keys(self.searchKeyword)
        searchForm.send_keys(Keys.ENTER)

    def _searchHasResults(self):
        try:
            noResultsText = self.session.find_element_by_class_name('search-no-results__message--muted-no-type Sans-21px-black-85% mb2')
            return False
        except NoSuchElementException:
            return True

    def _goToNextSearchResultsPage(self):
        try:
            nextButton = self.session.find_element_by_css_selector("button.next")
            self.session.execute_script("arguments[0].click();", nextButton)

            responseOk = self._checkResponseStatus()
            if not responseOk:
                return False

            return True
        except NoSuchElementException:
            return False

    def _checkResponseStatus(self):
        responseStatus = self._getResponseStatus()
        if responseStatus['statusText'] != 'ok':
            raise Exception("Could not connect to server. Status code: {}".format(responseStatus['status']))
            return False
        return True

    def _getResponseStatus(self):
        # FIX THIS
        return {'status': 200, 'statusText':'ok'}
