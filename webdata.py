#   webdata.py
#   Requests the data from the Warframe wiki
import requests
from pprint import pprint
from bs4 import BeautifulSoup
import os

#   The base url for the warframe wikia
wiki_url = 'https://warframe.fandom.com'

#   get_page
#   Returns a BeautifulSoup object for the given page
#   url:    The URL of the target page
def get_page(url):
    #print(url)
    req = requests.get(url)
    if (req.status_code != 200):
        return None
    return BeautifulSoup(req.content, 'html.parser')

#   data_saved
#   Returns True if there is a local copy of the data
def data_saved():
    return os.path.exists('data/data.txt')

#   data_expanded
#   Returns if the data has been expanded
#   data:   The data object to check
def data_expanded(data):
    return ('type' in data.keys())


#   get_data
#   Returns a dictionary of data
#   forced_refresh: If True, this forces a refresh from the wiki
def get_data(forced_refresh = False):
    if ((data_saved()) and (not forced_refresh)):
        return load_data()
    else:
        data = {}
        weapon_pages_url = [ '/wiki/Category:Weapons' ]
        contains_blacklist = ['Conclave', 'Category:', 'File:', 'PvP', 'User', 'Module:', 'Weapon']
        strict_blacklist = ['Arcata', 'Plague Kripath', 'Amp', 'Zaw', 'Kitgun']
        
        for url in weapon_pages_url:
            weapon_page = get_page(wiki_url + url)
            weapon_list = weapon_page.find('div', {'class': 'category-page__members'})
            weapon_entries = weapon_list.find_all('a', {'class': 'category-page__member-link'})
            for wep in weapon_entries:
                if ((len([bl for bl in contains_blacklist if bl in wep.attrs['title']]) == 0) and (not wep.attrs['title'] in strict_blacklist)):
                    data[wep.attrs['title'].lower()] = {
                        'name': wep.attrs['title'], 
                        'link': wep.attrs['href']
                    }
            next_page = weapon_page.find('a', {'class': 'category-page__pagination-next wds-button wds-is-secondary'})
            if (next_page != None):
                link = next_page.attrs['href'][len(wiki_url):]
                weapon_pages_url.append(link)
        return data

#   expand_data
#   Gathers additional information about the item
#   item: The dictionary item to expand
#   forced_refresh: If True this forces the data to update
def expand_data(item, forced_refresh = False):
    if ((data_expanded(item)) and (not forced_refresh)):
        return None
    #   Default Values
    item['mastery_rank'] = 0
    item['recipe'] = []
    item['blueprint_source'] = "No blueprint found"
    item['blueprint_cost'] = 0
    item['research'] = []

    item['type'] = "Undefined"
    item['slot'] = "Undefined"

    item_page = get_page(wiki_url + item['link'])
    sidebar = item_page.find('aside')
    if (sidebar != None):
        #   Find Mastery
        mastery_bar = sidebar.find('a', {'title': 'Mastery Rank'})
        if (mastery_bar != None):
            mastery = mastery_bar.parent.next_sibling.next_sibling.string
            item['mastery_rank'] = int(mastery)
        #   Find Slot
        slot_bar = sidebar.find('a', {'title': 'Weapons'})
        if (slot_bar != None):
            slot = slot_bar.parent.next_sibling.next_sibling.string
            item['slot'] = slot
        #   Find Type
        type_bar = sidebar.find('a', {'title': 'Mods'})
        if (type_bar != None):
            itype = type_bar.parent.next_sibling.next_sibling.string
            item['type'] = itype

    #   Crafting Information
    recipe_table = item_page.find('table', {'class':'foundrytable'})
    if (recipe_table != None):
        #   Blueprint cost
        blueprint_cost = recipe_table.find('a', {'title': 'Blueprints'})
        blueprint_cost = blueprint_cost.parent.contents[-1].strip()
        if (not 'Price' in blueprint_cost):
            item['blueprint_cost'] = int(blueprint_cost.replace(',', ''))

        #   Foundry recipe
        recipe_row = recipe_table.find('a', {'title':'Foundry'})
        if (recipe_row != None):
            recipe_row = recipe_row.parent.parent.next_sibling.next_sibling
            ingredients = [i.find('a') for i in recipe_row.find_all('td') if (i.find('a') != None)]
            for ing in ingredients:
                name = ing.attrs['title']
                count = int(ing.next_sibling.next_sibling.strip().replace(',', ''))
                item['recipe'].append((name, count))

        #   Clan research
        research_row = recipe_table.find('a', {'title':'Research'})
        if (research_row != None):
            #   Source
            item['blueprint_source'] = research_row.string
            #   Recipe
            research_row = research_row.parent.parent.next_sibling.next_sibling
            ingredients = [i.find('a') for i in research_row.find_all('td') if (i.find('a') != None)]
            for ing in ingredients:
                name = ing.attrs['title']
                count = int(ing.next_sibling.next_sibling.strip().replace(',', ''))
                item['research'].append((name, count))
        else:
            if ('Prime' in item['name']):
                #   Prime items come from relics
                item['blueprint_source'] = "Relics"
            else:
                if (item['blueprint_cost'] == 0):
                    #   Items that you can make but not by are special
                    item['blueprint_source'] = "Special"
                else:
                    #   Blueprints that are not dropped or researched come from the market
                    item['blueprint_source'] = "Market"
    else:
        #   Items with no blueprint are purchased
        #   Find the first paragraph
        acquired = item_page.find('span', {'id':'Acquisition'})
        paragraph = None
        if (acquired == None):
            acquired = item_page.find('a', {'title':'Credits'})
            if (acquired != None):
                paragraph = acquired.parent
        else:
            paragraph = acquired.parent.next_sibling.next_sibling

        #   Find the paragraph that mentions the cost
        while ((paragraph != None) and (len(paragraph.find_all('a', {'title':'Credits'})) == 0) and (paragraph.name == 'p')):
            paragraph = paragraph.next_sibling
            #   Find next paragraph
            while ((paragraph != None) and (paragraph.name != 'p')):
                paragraph = paragraph.next_sibling

        #   If such a paragraph exists, extract the relevant information
        if (paragraph != None):
            icons = paragraph.find_all('a', {'class', 'image image-thumbnail link-internal'})
            names = []
            for icon in icons:
                name = icon.attrs['title']
                if (not name in names):
                    count = int(icon.next_sibling.next_sibling.string.replace(',', ''))
                    item['recipe'].append((name, count))
                    names.append(name)
            if (names == ['Credits']):
                #   Items that take only credits are from the market
                item['blueprint_source'] = "Market" 
            elif ('Ducats' in names):
                #   Items that take ducats are from Baro
                item['blueprint_source'] = "Baro Ki'Teer"
            elif ('Standing' in names):
                #   Items that take standing are from factions
                item['blueprint_source'] = "Faction Standing"
                factions = [
                    ("Steel Meridian", "Vaykor"),
                    ("Arbiters of Hexis", "Telos"),
                    ("Cephalon Suda", "Synoid"),
                    ("Red Veil", "Rakta"),
                    ("New Loka", "Sancti"),
                    ("The Perrin Sequence", "Secura")
                ]
                for fac in factions:
                    if (fac[1] in item['name']):
                        item['blueprint_source'] += " (" + fac[0] + ")"


#   save_data
#   Saves the data to a local file
def save_data(data):
    if not (os.path.exists('data')):
        os.makedirs('data')
    f = open('data/data.txt', 'w')
    print(data, file = f)
    f.close()

#   load_data
#   Loads the data from a local file
def load_data():
    f = open('data/data.txt', 'r')
    data = eval(f.read())
    f.close()
    return data
    
