from bs4 import BeautifulSoup
import requests
import smtplib
import json

'''
check if a new cat is listed in the Animal Rescue League of Boston
'''
cat_dic = {} # cats' ids as keys, age info as values
new_kitten_info = [] # list of new cat info
 
newKitten = False
pageNumber = 1
# base_url without the page number
base_url = 'http://petharbor.com/results.asp?searchtype=ADOPT&start=2&stylesheet=http://www.arlboston.dbrowne.net/default1.css&friends=1&samaritans=1&nosuccess=0&orderby=Located&rows=10&imght=160&imgres=thumb&tWidth=200&view=sysadm.v_bstn&fontface=arial&fontsize=10&zip=02116&miles=200&shelterlist=%27BSTN%27&atype=&where=type_CAT&PAGE='

# function for parsing pages
def parse_page(page_url):
    # HTTP GET requests, add page number to parse each page
    page = requests.get(page_url + str(pageNumber))
    if page.status_code == requests.codes.ok: # Check if successfully fetched the URL
        soup = BeautifulSoup(page.text, 'lxml')
        # table that contains all the cats listed
        table = soup.find('table', class_='ResultsTable')
        # <img height="160" src="get_image.asp?RES=thumb&amp;ID=A274008&amp;LOCATION=BSTN" oncontextmenu="return false">
        # ID: A274008
        # <td class="TableContent2">05 Yrs<br/>00 Mos<br/>Spayed Female</td>
        # cat's info: 05 Yrs 00 Mos
        if table:
            for tr in table.find_all('tr')[1:]:
                ids = tr.find("img")["src"][27:34] # get ID number
                info = tr.find_all('td')[1].get_text(separator=' ') # get info
                cat_dic[ids] = info[:13] # retain only the age info

# function for saving dic in json file
def writeJson(dic):
    with open('cat_dic.json', 'w') as content:
        json.dump(dic, content)       

# function for sending pushbullet message
def pushbullet_message(title, body):
    msg = {"type": "note", "title": title, "body": body}
    TOKEN = '*************************' # get your TOKEN from https://www.pushbullet.com/#settings
    resp = requests.post('https://api.pushbullet.com/v2/pushes', 
                         data=json.dumps(msg),
                         headers={'Authorization': 'Bearer ' + TOKEN,
                                  'Content-Type': 'application/json'})
    if resp.status_code != 200:
        raise Exception('Error', resp.status_code)
    else:
        print ('Message sent') 

# Check the first 3 pages       
while pageNumber <= 3: 
    parse_page(base_url)
    pageNumber += 1
# writeJson(cat_dic) # write the first cat_dic

# read json file
with open('cat_dic.json', 'r') as f:
    old_cat_dic = json.load(f)

# check if new entries are added that's not in the old_cat_dic    
for i in cat_dic:
    if i not in old_cat_dic:
        new_kitten_info.append(cat_dic[i]) # store the new cat info
        print('NEW KITTEN!')
        newKitten = True

msg_title = 'NEW KITTEN!'
msg_body = '\n'.join(new_kitten_info)

# save new ids in cat_ids.json and send out a pushbullet message
if newKitten == True: 
    print(new_kitten_info)
    writeJson(cat_dic)
    pushbullet_message(msg_title, msg_body)
    
newKitten = False

# let the script run every 5 min from 8am to 8pm everyday with Windows Task Schduler


