#   webdata.py
#   Requests the data from the Warframe wiki
import requests
from pprint import pprint
from bs4 import BeautifulSoup

#   The base url for the warframe wikia
wiki_url = 'https://warframe.fandom.com'

#   get_page
#   Returns a BeautifulSoup object for the given page
#   url:    The URL of the target page
def get_page(url):
   req = requests.get(url)
   if (req.status_code != 200):
      return None
   return BeautifulSoup(req.content, 'html.parser')

#   data_saved
#   Returns True if there is a local copy of the data
def data_saved():
    pass

#   get_data
#   Returns a dictionary of data
#   forced_refresh: If true, this forces a refresh from the wiki
def get_data(forced_refresh = False):
    data = {}
    weapon_pages_url = {
        'primary':  '/wiki/Category:Primary_Weapons',
        'secondary':'/wiki/Category:Secondary_Weapons',
        'melee':    '/wiki/Category:Melee_Weapons'
    }
    title_blacklist = ['Conclave', 'Category:', 'File:', 'PvP', 'User blog:']
    
    for key, url in weapon_pages_url.items():
        weapon_page = get_page(wiki_url + url)
        weapon_list = weapon_page.find('div', {'class': 'category-page__members'})
        weapon_entries = weapon_list.find_all('a', {'class': 'category-page__member-link'})
        data[key] = {wep.attrs['title']:{'title': wep.attrs['title'], 'link': wep.attrs['href']} 
            for wep in weapon_entries
            if (len([bl for bl in title_blacklist 
                if bl in wep.attrs['title']]) == 0)}
    pprint(data)
        


#   save_data
#   Saves the data to a local file
def save_data(data):
    pass

#   load_data
#   Loads the data from a local file
def load_data():
    pass
