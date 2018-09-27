# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 00:33:19 2018

@author: kaany
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import csv
from datetime import datetime
from time import sleep

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
        self.session.implicitly_wait(3)

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
        with open("LinkedIn " + self.searchKeyword + ".csv", 
                  'w', newline='', encoding="utf-16") as csvfile:

            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

            writer.writerow(['Search Date', 'Keyword', 'Number of Results'])
            writer.writerow([datetime.today().strftime('%d-%m-%Y'), self.searchKeyword, len(data)])
            writer.writerow([])

            writer.writerow(['Name', 'Email', 'LinkedIn Profile Link'])

            for row in data:
                writer.writerow([row[0], row[1], row[2]])

    def _loadAllSearchResults(self):
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
            self.mainScraper.session.execute_script("arguments[0].click();", nextButton)

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
        return {'status': 200, 'statusText':'ok'}


class InvitationSender:

    def __init__(self, mainScraper):
        self.mainScraper = mainScraper

    def sendInvitationToAll(self):
        self.mainScraper._searchForKeyword()

        if self.mainScraper._searchHasResults == False:
            print("No search result found")
            return

        #Do while
        self._sendInvitationToPeopleOnCurrentPage()
        while (self.mainScraper._goToNextSearchResultsPage() and 
               self.mainScraper.numberOfProfilesScraped < self.mainScraper.personLimit):
            self._sendInvitationToPeopleOnCurrentPage()

    def _sendInvitationToPeopleOnCurrentPage(self):

        self.mainScraper._loadAllSearchResults()

        # Get all search results
        profileItems = self.mainScraper.session.find_elements_by_css_selector("li.search-result.search-result__occluded-item.ember-view")

        for item in profileItems:
            
            if self.mainScraper.numberOfProfilesScraped > self.mainScraper.personLimit:
                break
            
            profileName = item.find_element_by_css_selector("span.name.actor-name").text
            
            try:
                #Find and click the Connect button
                connectButton = item.find_element_by_css_selector("button.search-result__actions--primary.button-secondary-medium.m5")
                connectButton.click()
            except NoSuchElementException:
                #If there is no connect button, continue
                continue

            #Find and click to the Add a Note button
            addNoteButton = self.mainScraper.session.find_element_by_css_selector("button.button-secondary-large.mr1")
            addNoteButton.click()
            
            note = """Sayın {name}, bir yetenek havuzu olarak kullanacağımız
                    bu topluluğumuzda sizi yeni iş fırsatlarından
                    haberdar etmek için aramızda görmek istiyoruz.""".format(name=profileName)

            #Write the note
            noteTextArea = self.mainScraper.session.find_element_by_css_selector("textarea.send-invite__custom-message.mb3.ember-text-area.ember-view")
            noteTextArea.send_keys(note)
            
            #Send the invitation
            sendInvitationButton = self.mainScraper.session.find_element_by_css_selector("button.button-primary-large.ml1")
            sendInvitationButton.click()
            
            self.mainScraper.numberOfProfilesScraped += 1
        

class ProfileScraper:

    def __init__(self, mainScraper):
        self.mainScraper = mainScraper

    def scrapeAllProfileLinks(self):
        self.mainScraper._searchForKeyword()

        allProfileLinks = []

        if self.mainScraper._searchHasResults == False:
            print("No search result found")
            return allProfileLinks

        # Do while
        profileLinks = self.getProfileLinksOnPage()
        allProfileLinks.append(profileLinks)
        while (self.mainScraper._goToNextSearchResultsPage() and 
               self.mainScraper.numberOfProfilesScraped < self.mainScraper.personLimit):
            profileLinks = self.getProfileLinksOnPage()
            allProfileLinks.append(profileLinks)

        allProfileLinks = [link for links in allProfileLinks for link in links]

        return allProfileLinks

    def getProfileLinksOnPage(self):
        self.mainScraper._loadAllSearchResults()

        #Find all search results
        profileItems = self.mainScraper.session.find_elements_by_css_selector("li.search-result.search-result__occluded-item.ember-view")

        profileLinks = []

        for profileItem in profileItems:
            if self.mainScraper.numberOfProfilesScraped > self.mainScraper.personLimit:
                return profileLinks

            if self.mainScraper._isNameLinkedInMember(profileItem):
                continue

            #Find anchor tag containing the search result's profile link
            anchorTag = profileItem.find_element_by_css_selector("a.search-result__result-link.ember-view")
            profileLink = anchorTag.get_attribute('href')
            profileLinks.append(profileLink)

            self.mainScraper.numberOfProfilesScraped += 1

        return profileLinks
    
    def _extractInfoFromProfileLinks(self, profileLinks):
        data = []
        for link in profileLinks:
            person = self._extractInfo(link)
            data.append((person.name, person.email, person.profileLink))

        return data
    
    def _extractInfo(self, profileLink):
        self.mainScraper.session.get(profileLink)
        
        responseOk = self.mainScraper._checkResponseStatus()
        if not responseOk:
            return False
        
        nameDiv = self.mainScraper.session.find_element_by_css_selector("div.pv-top-card-v2-section__info.mr5")
        name = nameDiv.find_element_by_tag_name("h1").text

        contactInfoLink = self.mainScraper.session.current_url + 'detail/contact-info/'

        contactInfo = self._extractContactInfo(contactInfoLink)

        return Person(name, contactInfo['email'], profileLink)

    def _extractContactInfo(self, contactInfoLink):
        self.mainScraper.session.get(contactInfoLink)

        responseOk = self.mainScraper._checkResponseStatus()
        if not responseOk:
            return None
        
        try:
            emailDiv = self.mainScraper.session.find_element_by_css_selector("section.pv-contact-info__contact-type.ci-email")
        except NoSuchElementException:
            return {'email': 'None'}

        email = emailDiv.find_element_by_tag_name("a").get_attribute('href')
        email = email.split(":")[1]

        return {'email': email}


class Person:

    def __init__(self, name, email, profileLink):
        self.name = name
        self.email = email
        self.profileLink = profileLink
