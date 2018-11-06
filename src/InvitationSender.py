

class InvitationSender:

    def __init__(self, mainScraper):
        self.mainScraper = mainScraper

    def sendInvitationToAll(self):
        self.mainScraper._searchForKeyword()

        if self.mainScraper._searchHasResults == False:
            print("No search result found")
            return

        #Do while
        self._sendInvitationToPersonOnCurrentPage()
        while (self.mainScraper._goToNextSearchResultsPage() and
               self.mainScraper.numberOfProfilesScraped < self.mainScraper.personLimit):
            self._sendInvitationToPersonOnCurrentPage()

    def _sendInvitationToPersonOnCurrentPage(self):

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
