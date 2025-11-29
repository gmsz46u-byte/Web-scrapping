# importing imp modules
from selenium import  webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import datetime
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import re
import json
import schedule

### Setting wd as general variable to be easily accessed by all functions
path = 'C:\\Users\\TOUCH\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\edgedriver_win64\\msedgedriver.exe' 
edgeOPtions = Options()
edgeOPtions.add_argument("headless")
edgeOPtions.add_argument("--no-sandbox")
edgeOPtions.add_argument("--disable-dev-shm-usage")
edgeOPtions.add_argument("user-agent=Mozilla/5.0(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTM, like Gecko) Chrome/115.0.0.0 Safari/537.36")
edgeOPtions.add_argument("--start-maximized")
edgeServices = Service(path)
wd = webdriver.Edge(edgeOPtions,edgeServices)
action = ActionChains(wd)
wd.implicitly_wait(8)




### setting bs4 
headers = {
    "accept" : "*/*",
    "accept-encoding":"gzip, deflate, br, zstd",
    "accept-language":"en-US,en;q=0.9,ar;q=0.8",
    "user-agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36 Edg/142.0.0.0" } ## most imp line

## Declaring todays_date
DateCheck = datetime.datetime.now().date().strftime("%d_%m_%Y")

### preparing df
columns = ['DateCheck','Market','product_id','product_name','Price','Rating','Link']
df = pd.DataFrame(columns=columns)

### create csv file at end of project
def create_excel():
    file_name = f'Search_for_{search_name}_at_{DateCheck}.xlsx'
    df.to_excel(file_name,index=False)
    print("Excel file with name {0} succesfully created".format(file_name))

### adding data into declared df
def info_into_df(whole_products_info): ### whole_products_info is a list with many dict for each product
    for product_info in whole_products_info:
        if list(product_info.keys())==columns:
            df.loc[len(df)] = [product_info[str(x)] for x in columns]

### alibaba Main page search function
def alibaba_page_search(search_name:str,page):
    base_url = "https://www.alibaba.com/trade/search?spm=a2700.product_home_newuser.home_new_user_first_screen_fy23_pc_search_bar.associationItem_pos_0&tab=all&SearchText={0}&has4Tab=true".format(search_name.replace(" ","+"))
    wd.get(base_url)
    # wd.maximize_window()
    time.sleep(12)
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    if page > 1:
        try: 
            action.move_to_element(wd.find_element(By.CSS_SELECTOR,"div.searchx-pagination-list > a:nth-child(%s)"%(str(page)))).click().perform()
            time.sleep(10)
        except: print('alibaba next page not found')
    try : 
        cards = wd.find_elements(By.CSS_SELECTOR,"div.fy26-product-card-wrapper")
        products_data = []
        time.sleep(3)
        if len(cards) != 0 :
            for card in cards :
                    try : link = card.find_element(By.TAG_NAME,"a").get_attribute('href')
                    except:link = None
                    card_content = card.find_element(By.CSS_SELECTOR,"div.fy26-product-card-content")
                    try : product_name = card_content.find_element(By.CSS_SELECTOR,"h2.searchx-product-e-title>a>span").text
                    except: product_name = None
                    try : price = card_content.find_element(By.CSS_SELECTOR,"div:nth-child(2) a div div.searchx-product-price-price-main").text
                    except: price = None
                    try : min_order = card_content.find_element(By.CSS_SELECTOR,"div:nth-child(3) div").text
                    except: min_order = None
                    try: product_id = card.get_attribute("data-ctrdot")
                    except:product_id = None
                    try : rating = card.find_element(By.CSS_SELECTOR,"span.searchx-product-e-review span.searchx-review-score").text
                    except : rating = None
                    product_info = {
                        'DateCheck': DateCheck,
                        'Market':'alibaba',
                        'product_id':product_id,
                        'product_name':product_name,
                        'Price':price,
                        'Rating':rating,
                        'Link':link,
                    }
                    products_data.append(product_info)
            info_into_df(products_data)
    except: print('alibaba no found page')
        
### eBay Main Page search function
def ebay_page_search(search_name,page):
    url = 'https://www.ebay.com/sch/i.html?_nkw=' + search_name + '&_sacat=0&_from=R40&_pgn=' + str(page)
    wd.get(url)
    time.sleep(3)
    all_products = wd.find_elements(By.CSS_SELECTOR,"div#srp-river-results > ul > li")
    time.sleep(4)
    products_data = []
    if len(all_products) != 0 :
        for product in all_products:
            try:
                product_id = product.get_attribute("data-listingid")
                product_name = product.find_element(By.CSS_SELECTOR,"a > div > span").text
                attrs = [x.text for x in (product.find_elements(By.CSS_SELECTOR,"div.s-card__attribute-row > span")) ]## not always the same and changes bet products ['$161.97', 'or Best Offer', '+$21.98 delivery', 'Located in Italy', '273 sold', 'bitsmart_technology_italy', '100% positive (152)']
                if attrs :
                    price = attrs[0] if attrs[0] else ''
                    delivery_fee = attrs[2] if attrs[2] else ''
                    ratings = attrs[-1] if attrs[-1] else ''
                    link = product.find_element(By.TAG_NAME,'a').get_attribute('href')
                    product_info = {
                        'DateCheck':DateCheck,
                        'Market':'eBay',
                        'product_id':product_id,
                        'product_name':product_name,
                        'Price': (price + ' (%s)' %(delivery_fee)),
                        'Rating':ratings,
                        'Link':str(link),
                    }
                else : print('no found data')
            except:
                print('ebay some exception // data not added')
            else : 
                products_data.append(product_info)
    else:print('ebay empty page')
    time.sleep(4)
    info_into_df(products_data)

### Walmart search main page
def walmart_page_search(search_name,page):
    page = str(page)
    search_url = 'https://www.walmart.com/search?q=' + search_name + f'&page={page}&affinityOverride=default'
    response = requests.get(search_url,headers=headers)
    time.sleep(3)
    soup = BeautifulSoup(response.text,'html.parser')
    page_json = soup.find("script",id="__NEXT_DATA__")
    page_content = json.loads(page_json.string)
    products_data = (page_content['props']['pageProps']['initialData']['searchResult']['itemStacks']) ## a list  / len == 8
    whole_products_info = [] ## list to containt all info
    for grouped_products in products_data: #### grouped_products data == reached by trial and error of code and is a list // len == 5
        for product_data in grouped_products['items']:   ## grouped products is a dict with key item contain all data
            try:
                product_info = {
                    'DateCheck':DateCheck,
                    'Market':'Walmart',
                    'product_id':product_data['id'],
                    'product_name':product_data['name'],
                    # 'img_thumbnailurl':product_data['imageInfo']['thumbnailUrl'],
                    #### 'discounts':product_data['discounts'], not always present so gives mx errors
                    # 'price':product_data['discounts']['linePrice'],
                    # 'wasPrice':product_data['discounts']['wasPrice'],
                    # 'savings':product_data['discounts']['savings'],
                    ## 'badges' : product_data['badges'] ## for deals like HOLIday deal // Blackfriday deal info
                    ## 'priceInfo': product_data['priceInfo'] , >>  {'itemPrice': '$81.99', 'linePrice': 'Now $63.99', 'linePriceDisplay': 'Now $63.99', 'savings': 'SAVE $18.00', 'savingsAmt': 18, 'wasPrice': '$81.99', 'wasPriceSupportText': '', 'unitPrice': '', 'shipPrice': '', 'minPrice': 63.99, 'minPriceForVariant': '', 'priceRangeString': 'From $63.99', 'subscriptionPrice': '', 'subscriptionString': '', 'subscriptionDiscountPrice': '', 'priceDisplayCondition': '', 'finalCostByWeight': False, 'submapType': '', 'eaPricingText': '', 'eaPricingPreText': '', 'memberPriceString': '', 'subscriptionDualPrice': None, 'subscriptionPercentage': None, 'isB2BPrice': False, 'dutyFee': None, 'priceDisplayType': 'UNKNOWN'}
                    # 'item_price':product_data['priceInfo']['itemPrice'],
                    'Price':product_data['priceInfo']['linePrice'],
                    # 'wasPrice':product_data['priceInfo']['wasPrice'],
                    ## 'members' : product_data['groups']==(list) >> ['members'] ## for shippment details
                    'Rating':product_data['averageRating'],
                    # 'numberOfReviews':product_data['numberOfReviews'],
                    # 'sellerId':product_data['sellerId'],
                    # 'sellerName':product_data['sellerName'],
                    # 'availabilityStatusV2':product_data['availabilityStatusV2'],  >> {'display': 'In stock', 'value': 'IN_STOCK'}
                    'Link': 'https://www.walmart.com/' + product_data['canonicalUrl'],
                }
            except: 
                print('walmart error')
            else : 
                whole_products_info.append(product_info)
    info_into_df(whole_products_info)


### Amazon Main search function for every page
def amazon_page_search(search_name,page):
    url = 'https://www.amazon.eg/s?k=' + search_name + '&page=' + str(page)
    wd.get(url)
    time.sleep(3)
    all_products = wd.find_elements(By.CSS_SELECTOR,"div[role='listitem']")
    products_data = []
    if len(all_products) != 0:
        for product in all_products:
            ## Handling exceptions due to missing products (due to presence of ads in search pages)
            try:
                Market = 'Amazon'
                try : product_asin = product.get_attribute("data-asin")
                except : product_asin = None
                if product_asin:
                    # product_id = product.get_attribute("id")
                    # product_uuid = product.get_attribute("data-uuid")
                    try : product_name = product.find_element(By.CSS_SELECTOR,"h2 span").text.replace(","," ")
                    except:product_name = None
                    try : product_price = product.find_element(By.CLASS_NAME,"a-price-whole").text
                    except:product_price = None
                    try : product_currency = product.find_element(By.CLASS_NAME,"a-price-symbol").text
                    except: product_currency = None
                    # product_rating = product.find_element(By.CLASS_NAME,"a-declarative").find_element(By.TAG_NAME,"i").text  ### NOt working
                    product_rating = ''
                    # product_rating = product.find_element(By.XPATH,"//div[@data-cy='reviews-block']/span/a/span[1]").text  ### NOt working
                    try : link_to_product = product.find_element(By.CLASS_NAME,"a-link-normal").get_attribute("href")
                    except: link_to_product = None
            except:
                print('amazon some exception // data not added')
            else :
                price = str(product_price) + str(product_currency)
                product_info = {
                    'DateCheck':DateCheck,
                    'Market' : Market,
                    'product_id' : product_asin,
                    'product_name' : product_name,
                    'Price' : price,
                    'Rating':product_rating,
                    'Link':link_to_product,
                }
                products_data.append(product_info)
        info_into_df(products_data)
    else : print('amazon empty page')

## search name will be put as an input in future
search_name = 'tablet'
page = 1   

## Loop for continous scraping for first ??? pages
while True:
    ##################### Good working interval 3min for webs to avoid get panned from scraping  #####################
    time.sleep(180)
    amazon_page_search(search_name,page)
    alibaba_page_search(search_name,page)
    ebay_page_search(search_name,page)
    walmart_page_search(search_name,page)
    # break
    time.sleep(10)
    ### increasing page num after scraping
    page+=1
    ### if pages > target num of pages : stop looping
    if page > 3:
        ### creating excel file before breaking tool
        create_excel()
        ### terminating selenium webdriver
        wd.quit()
        break

