

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
