
from selenium import webdriver
from bs4 import BeautifulSoup as BS
import pprint, json, os

def getSoup(url):
    driver = webdriver.Chrome('/usr/local/share/chromedriver')
    driver.get(url)
    response = driver.execute_script("return document.documentElement.outerHTML")
    driver.quit()
    soup = BS(response,'html.parser')
    return soup

'''
***************
    Task 1
***************
'''
def scrapeLocalities():
    soup = getSoup('https://www.zomato.com/ncr')
    MainDiv = soup.find('div',class_='ui segment row')
    all_localities = MainDiv.find_all('a')
    popular_localities = []
    for location in all_localities:
        url = location.get('href')
        locName = location.get_text().strip().split()
        locName.pop(-1)
        no_places = int(locName[-1].strip("("))
        locName.pop(-1)
        place_name = " ".join(locName)
        locality = {
        'placeName': place_name,
        'places': no_places,
        'url':url
        }
        popular_localities.append(locality)
    return popular_localities

Localities = scrapeLocalities()
# pprint.pprint(Localities)

'''
***************
    Task 2
***************
'''

Places = {}
def getPlaceDetails(place):

    fileName = ''.join(place['placeName'].split())
    if os.path.exists('cache/' + fileName + '.json'):
        with open('cache/' + fileName + '.json') as file:
            text = file.read()
            allData = json.loads(text)
            return allData

    Places['placeName'] = place['placeName']
    Places['restDetails'] = []
    soup = getSoup(place['url'])
    see_more = soup.find_all('a',class_='zred')

    for link in see_more:
        soup = getSoup(link.get('href'))
        details = {}
        details['title'] = soup.find('h1',class_='search_title').get_text().strip()
        details['details'] = []
        divsList = soup.find('div', attrs = {'id':'orig-search-list','class':'ui cards'})
        allDivs = divsList.find_all('div', class_='search-snippet-card')
        for div in allDivs:
            restDetail ={}

            ratingVotes = div.find('div',class_='search_result_rating').get_text().strip().split()
            otherDetails = div.find('div', class_='search-page-text')
            cuisines = otherDetails.find('div',class_='clearfix')
            allCuisines = cuisines.find_all('a')
            cost = otherDetails.find('div', class_='res-cost')

            restDetail['restaurantName'] = div.find('a',class_='hover_feedback').get_text().strip()
            restDetail['location'] = div.find('a', class_='zblack').get_text().strip()
            restDetail['address']= div.find('div', class_='search-result-address').get_text().strip()
            if len(ratingVotes) >1:
                restDetail['rating'] = ratingVotes[0]
                restDetail['votes'] = ratingVotes[1]
            print(cost)
            if cost != None:
                cost = cost.get_text().strip().split()
                restDetail['cost'] = int(''.join(cost[2].strip('two:₹').split(',')))
            restDetail['cuisines'] = [cuisines.get_text().strip() for cuisines in allCuisines]

            details['details'].append(restDetail)
        Places['restDetails'].append(details)

    with open('cache/' + fileName + '.json','w') as content:
        raw = json.dumps(Places, indent=4, sort_keys=True)
        content.write(raw)
        content.close()
    return Places


# placeDeatails = getPlaceDetails(Localities[0])
# pprint.pprint(placeDeatails)

'''
***************
    Task 3
***************
'''

def getAllLocalities(placeslist):
    allRestDetails = []
    for location in placeslist:
        placeDetails = getPlaceDetails(location)
        allRestDetails.append(placeDetails)
    return allRestDetails

allPlaceDetails = getAllLocalities(Localities)
pprint.pprint(allPlaceDetails)
