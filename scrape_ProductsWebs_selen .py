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
### Setting wd as general variable to be easily accessed by all functions
path = 'C:\\Users\\TOUCH\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\edgedriver_win64\\msedgedriver.exe' 
edgeOPtions = Options()
# edgeOPtions.add_argument("headless")
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
columns = ['DateCheck','Market','product_id','product_name','Price','Rating','Img_src','Link']
main_df = pd.DataFrame(columns=columns)

### create csv file at end of project
def create_excel():
    file_name = f'Search_for_{search_name}_at_{DateCheck}.xlsx'
    dfs_new_list =[]
    for x in dfs_list:
        dfs_new_list.append(x)
    new_df = pd.concat(dfs_new_list,axis=0)
    print(new_df)
    with pd.ExcelWriter(file_name) as writer:
        new_df.to_excel(writer,index=False,sheet_name='{0}'.format(DateCheck))
    print("Excel file with name {0} succesfully created".format(file_name))

### adding data into declared df
dfs_list = []
def info_into_df(whole_products_info): ### whole_products_info is a list with many dict for each product
    df = pd.DataFrame(data=whole_products_info,columns=columns)
    dfs_list.append(df)

### Amazon Main search function for every page
def amazon_page_search(search_name,page):
    products_data = []
    while True:
        if page == 1 :
            url = 'https://www.amazon.eg/s?k=' + search_name + '&page=' + str(page)
            wd.get(url)
        time.sleep(10)
        all_products = wd.find_elements(By.CSS_SELECTOR,"div[role='listitem']")
        if len(all_products) != 0:
            for product in all_products:
            ## Handling exceptions due to missing products (due to presence of ads in search pages)
                Market = 'Amazon'
                try : product_asin = product.get_attribute("data-asin")
                except : product_asin = None
                if product_asin:
                    try : product_name = product.find_element(By.CSS_SELECTOR,"h2 span").text.replace(","," ")
                    except:product_name = None
                    try : product_price = product.find_element(By.CLASS_NAME,"a-price-whole").text
                    except:product_price = None
                    try : product_currency = product.find_element(By.CLASS_NAME,"a-price-symbol").text
                    except: product_currency = None
                    product_rating = ''
                    try : link_to_product = product.find_element(By.CLASS_NAME,"a-link-normal").get_attribute("href")
                    except: link_to_product = None
                    try : img = product.find_element(By.TAG_NAME,"img").get_attribute('src')
                    except:img=None
                    price = str(product_price)
                    product_info = {
                        'DateCheck':DateCheck,
                        'Market' : Market,
                        'product_id' : product_asin,
                        'product_name' : product_name,
                        'Price' : price,
                        'Rating':product_rating,
                        'Img_src':img,
                        'Link':link_to_product,
                    }
                    products_data.append(product_info)
            print(products_data)
        else : print('amazon empty page')
        # check to close after some point
        page+=1
        if page > 5:
            info_into_df(products_data)
            # create_excel()
            wd.quit()
            break
        ## going down to bottom of screen
        time.sleep(3)
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(5)
        ## change to next page
        pagination_list = wd.find_element(By.CSS_SELECTOR,"div[aria-label='pagination'] span[class='s-pagination-strip'] ul")
        page_lis = pagination_list.find_elements(By.XPATH,"./*")
        for page_li in page_lis:
            try : 
                target_a = page_li.find_element(By.CSS_SELECTOR,"li span a")
                if target_a.text == str(page):
                    # print(page_lis.index(page_li))
                    action.move_to_element(wd.find_element(By.CSS_SELECTOR,"div[aria-label='pagination'] span[class='s-pagination-strip'] ul li:nth-child(%s)"%str((page_lis.index(page_li))+1))).click().perform()
                    break
            except : pass
        time.sleep(10)

### alibaba Main page search function
def alibaba_page_search(search_name:str,page):
    ## trying to mimic user action by searching main page for product
    wd.get('https://www.alibaba.com/')
    time.sleep(3)
    wd.find_element(By.XPATH,"//div[contains(@class, 'home-search')]//input").send_keys(search_name)
    time.sleep(2)
    wd.find_element(By.XPATH,"//div[contains(@class,'home-search')]//input").send_keys(Keys.ENTER)
    time.sleep(12)
    products_data = []
    while True:
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)
        try : 
            cards = wd.find_elements(By.CSS_SELECTOR,"div.fy26-product-card-wrapper")
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
                    try: img= card.find_element(By.CSS_SELECTOR,".searchx-img-area img").get_attribute('src')
                    except: img = ''
                    product_info = {
                        'DateCheck': DateCheck,
                        'Market':'alibaba',
                        'product_id':product_id,
                        'product_name':product_name,
                        'Price':price,
                        'Rating':rating,
                        'Img_src':img,
                        'Link':link,
                    }
                    products_data.append(product_info)
        except: print('alibaba no found page')
        page+=1
        if page > 5 :
            info_into_df(products_data)
            break
        if page > 1:
            for i in range(3):
                try: 
                    action.move_to_element(wd.find_element(By.CSS_SELECTOR,"div.searchx-pagination-list > a:nth-child(%s)"%(str(page)))).click().perform()
                    time.sleep(10)
                    break
                except: 
                    print('alibaba next page not found')
                    wd.refresh()
                    time.sleep(5)
                
### eBay Main Page search function
def ebay_page_search(search_name,page):
    if page == 1 :
        url = 'https://www.ebay.com/'
        wd.get(url)
        wd.find_element(By.XPATH,"//div[@id='gh-search-box']//input").send_keys(search_name.replace(" ","+"))
        time.sleep(2)
        wd.find_element(By.XPATH,"//div[@id='gh-search-box']//input").send_keys(Keys.ENTER)
    products_data = []
    while True:
        time.sleep(10)
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        soup = BeautifulSoup(wd.page_source,'html.parser')
        soup_products = soup.select("div#srp-river-results > ul > li")
        time.sleep(4)
        if len(soup_products) != 0 :
            for prod in soup_products:
                try:
                    product_id = prod.get("data-listingid")
                    product_name = prod.select_one("a > div > span").get_text()
                    img = prod.select_one("li img").get('src')
                    attrs = [x.get_text() for x in (prod.select("div.s-card__attribute-row > span")) ]## not always the same and changes bet products ['$161.97', 'or Best Offer', '+$21.98 delivery', 'Located in Italy', '273 sold', 'bitsmart_technology_italy', '100% positive (152)']
                    if attrs :
                        price = attrs[0] if attrs[0] else ''
                        delivery_fee = attrs[2] if attrs[2] else ''
                        ratings = attrs[-1] if attrs[-1] else ''
                        link = prod.find('a').get('href')
                        product_info = {
                            'DateCheck':DateCheck,
                            'Market':'eBay',
                            'product_id':product_id,
                            'product_name':product_name,
                            'Price': (price + ' (%s)' %(delivery_fee)),
                            'Rating':ratings,
                            'Img_src':img,
                            'Link':str(link),
                        }
                    else : print('no found data')
                except:
                    print('ebay some exception // data not added')
                    
                else : 
                    products_data.append(product_info)
        else:print('ebay empty page')
        time.sleep(4)
        page+=1
        if page> 5:
            info_into_df(products_data)
            break
        if page > 1:
            # scroll down 
            wd.execute_script('window.scrollTo(0 , document.body.scrollHeight)')
            time.sleep(1)
            # move to next page
            paginaiton_item = wd.find_element(By.CLASS_NAME,"pagination__items")
            #get all li pagintaion items to search for text == page number
            page_lis = paginaiton_item.find_elements(By.XPATH,"./*")
            for page_li in page_lis :
                try: 
                    target_a = page_li.find_element(By.CSS_SELECTOR,'li a')
                    if target_a.text == str(page):
                        action.move_to_element(wd.find_element(By.CSS_SELECTOR,".pagination__items > li:nth-child(%s)"%(str(page_lis.index(page_li)+1)))).click().perform()
                        break
                except: pass

### Walmart search  page
def walmart_page_search(search_name,page):
    whole_products_info = [] ## list to containt all info
    while True:
        search_url = 'https://www.walmart.com/search?q=' + search_name + f'&page={str(page)}&affinityOverride=default'
        response = requests.get(search_url,headers=headers)
        time.sleep(3)
        soup = BeautifulSoup(response.text,'html.parser')
        page_json = soup.find("script",id="__NEXT_DATA__")
        page_content = json.loads(page_json.string)
        products_data = (page_content['props']['pageProps']['initialData']['searchResult']['itemStacks']) ## a list  / len == 8
        for grouped_products in products_data: #### grouped_products data == reached by trial and error of code and is a list // len == 5
            for product_data in grouped_products['items']:   ## grouped products is a dict with key item contain all data
                try:
                    product_info = {
                        'DateCheck':DateCheck,
                        'Market':'Walmart',
                        'product_id':product_data['id'],
                        'product_name':product_data['name'],
                        'Price':product_data['priceInfo']['linePrice'],
                        'Rating':product_data['averageRating'],
                        'Img_src':product_data['imageInfo']['thumbnailUrl'],
                        'Link': 'https://www.walmart.com/' + product_data['canonicalUrl'],
                    }
                except: 
                    print('walmart error')
                else : 
                    whole_products_info.append(product_info)
        page+=1
        if page > 5:
            print(whole_products_info)
            info_into_df(whole_products_info)
            break
            
search_name = 'laptops' ## can be anyname / to be changed to input by user
page = 1   ## search is limited to 5 pages within functions , can be changed to adapt needs

if __name__ == "__main__":
    amazon_page_search(search_name,page)
    alibaba_page_search(search_name,page)
    ebay_page_search(search_name,page)
    walmart_page_search(search_name,page)
    create_excel()
