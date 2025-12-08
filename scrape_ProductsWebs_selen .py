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

### alibaba Main page search function
def alibaba_page_search(search_name:str,page):
    # url = 'https://www.alibaba.com/trade/search?spm=a2700.product_home_newuser.home_newuser_first_screen_fy23_pc_search_bar.associationItem_pos_0&tab=alt&SearchText=E' + search_name 
    # base_url = "https://www.alibaba.com/trade/search?spm=a2700.product_home_newuser.home_new_user_first_screen_fy23_pc_search_bar.associationItem_pos_0&tab=all&SearchText={0}&has4Tab=true".format(search_name.replace(" ","+"))
    ## to bypass alibaba prb with automation
    wd.get('https://www.alibaba.com/')
    time.sleep(3)
    wd.find_element(By.XPATH,"//div[contains(@class, 'home-search')]//input").send_keys(search_name.replace(" ","+"))
    time.sleep(2)
    wd.find_element(By.XPATH,"//div[contains(@class,'home-search')]//input").send_keys(Keys.ENTER)
    time.sleep(12)
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    if page > 1:
        try: 
            action.move_to_element(wd.find_element(By.CSS_SELECTOR,"div.searchx-pagination-list > a:nth-child(%s)"%(str(page)))).click().perform()
            time.sleep(10)
        except: print('alibaba next page not found')

    try : 
        cards = wd.find_elements(By.CSS_SELECTOR,"div.fy26-product-card-wrapper")
        # print(len(cards))
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

                    # print(products_data)
            # print(products_data)
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
                img = product.find_element(By.CSS_SELECTOR,"li img").get_attribute('src')
                attrs = [x.text for x in (product.find_elements(By.CSS_SELECTOR,"div.s-card__attribute-row > span")) ]## not always the same and changes bet products ['$161.97', 'or Best Offer', '+$21.98 delivery', 'Located in Italy', '273 sold', 'bitsmart_technology_italy', '100% positive (152)']
                # [price,offer,delivery_fee,location,num_sold,selllerName,ratings] = attrs  ## raises error as len(attrs) is changing () products
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
                        'Img_src':img,
                        'Link':str(link),
                    }
                else : print('no found data')
            ## great exception code to view the errorType
            # except Exception as ex:
            #     template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            #     message = template.format(type(ex).__name__, ex.args)
            #     print(message)
            except:
                print('ebay some exception // data not added')
                
            else : 
                products_data.append(product_info)
    else:print('ebay empty page')
    time.sleep(4)
    # print(products_data)
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
    # print(page_content['props']['pageProps']['initialData']['searchResult']['paginationV2']['maxPage'])  ### returs max page of search for product // but not accurate as higher pages are mostly broken
    products_data = (page_content['props']['pageProps']['initialData']['searchResult']['itemStacks']) ## a list  / len == 8
    whole_products_info = [] ## list to containt all info
    # if len(product_data) != 0 :
    for grouped_products in products_data: #### grouped_products data == reached by trial and error of code and is a list // len == 5

        """product_data == 
        {'__typename': 'Product', 'buyBoxSuppression': False, 'similarItems': False, 'id': '5CW9XGXVINYR', 'usItemId': '16370069035', 'isBadSplit': False, 'fitmentLabel': None, 'name': '10.1 Inch HD Octa-Core 
Processor Android Tablet,10GB RAM,64 GB ROM, BT 5.0, Dual Camera, Gray Office & Student Tablet Computer（S10）', 'checkStoreAvailabilityATC': False, 'seeShippingEligibility': False, 'brand': None, 'type': 'VARIANT', 'shortDescription': None, 'averageWeight': None, 'weightIncrement': 1, 'topResult': None, 'additionalOfferCount': None, 'availabilityInNearbyStore': None, 'itemBeacon': None, 'catalogProductType': 'Tablet Computers', 'collectibles': None, 'gradingTypeCode': None, 'conditionPriceRange': None, 'imageInfo': {'id': 'B9450E52DC054DB5957549ED91A2DD11', 'name': '10-1-Inch-HD-Processor-Gray-Android-Tablet-10GB-RAM-64-GB-ROM-BT-5-0-Dual-Camera-Office-Tablet-Computer-Gray_c88cb895-2778-48bd-9ffd-223ae43c1477.6ed6753b90896ee7ceca1be9e89b1e6e.jpeg', 'thumbnailUrl': 'https://i5.walmartimages.com/seo/10-1-Inch-HD-Processor-Gray-Android-Tablet-10GB-RAM-64-GB-ROM-BT-5-0-Dual-Camera-Office-Tablet-Computer-Gray_c88cb895-2778-48bd-9ffd-223ae43c1477.6ed6753b90896ee7ceca1be9e89b1e6e.jpeg?odnHeight=180&odnWidth=180&odnBg=FFFFFF', 'size': '104-104', 'allImages': []}, 'aspectInfo': {'name': None, 'header': None, 'id': None, 'snippet': None}, 'plItem': {'isPLItemToBoost': False, 'plItemTagString': ''}, 'canonicalUrl': '/ip/10-1-Inch-HD-Processor-Gray-Android-Tablet-10GB-RAM-64-GB-ROM-BT-5-0-Dual-Camera-Office-Tablet-Computer-Gray/16370069035?classType=VARIANT&athbdg=L1800', 'conditionV2': {'code': 1, 'groupCode': 1}, 'externalInfo': None, 'itemType': None, 'category': {'categoryPathId': '0:3944:1078524:1231200:9141291', 'path': None}, 'returnPolicy': {'returnable': None, 'freeReturns': None, 'returnWindow': {'value': None, 'unitType': 'Day'}, 'returnPolicyText': None}, 'discounts': {'id': 'CONFIG_PROMO', 'linePrice': '$60.99', 'linePriceDisplay': 'Now est. $60.99', 'savings': '$21.00', 'savingsAmt': 21, 'wasPrice': '$81.99', 'comparisonPrice': '$81.99', 'unitPrice': None, 'priceDisplayCondition': None}, 'badges': {'flags': [{'__typename': 'BaseBadge', 'key': 'HOLIDAY_DEAL', 'text': 'Black Friday Deal', 'type': 'LABEL', 'id': 'L1800', 'styleId': 'PRIMARY_OZARKNOIR_BOLD'}], 'tags': [{'__typename': 'BaseBadge', 'key': 'SAVE_WITH_W_PLUS', 'text': 'Save with', 'type': 'ICON'}], 'groups': [{'__typename': 'UnifiedBadgeGroup', 'name': 'fulfillment', 'members': [{'__typename': 'BadgeGroupMember', 'id': 'L1053', 'key': 'FF_SHIPPING', 'memberType': 'badge', 'otherInfo': None, 'rank': 1, 'textTemplate': None, 'textValues': None, 'slaText': 'in 3+ days', 'slaDate': None, 'slaDateISO': None, 'sla': None, 'styleId': 'FF_STYLE', 'text': 'Free shipping, arrives ', 'type': None, 'iconId': None, 'templates': None, 'badgeContent': None}]}], 'groupsV2': [{'name': 'flags', 'flow': 'HORIZONTAL', 'pos': 'ProdTileBadgeModule1', 'members': [{'memType': 'badge', 'memId': 'L1800', 'memStyleId': 'PRIMARY_MIDNIGHTBLUE', 'fbMemStyleId': None, 'content': [{'type': 'TEXT', 'value': 'Black Friday Deal', 'styleId': 'WHITE_BOLD', 'fbStyleId': None, 'contDesc': None, 'url': None, 'actionId': None}]}]}]}, 'buyNowEligible': True, 'classType': 'VARIANT', 'averageRating': 4, 'numberOfReviews': 274, 'esrb': None, 'mediaRating': None, 'salesUnitType': 'EACH', 'sellerId': '5B06653A803442CFBDA6E2559B9E57F1', 'sellerName': 'Shanjing', 'sellerType': None, 'hasSellerBadge': None, 'isEarlyAccessItem': True, 'preEarlyAccessEvent': True, 'earlyAccessEvent': False, 'blitzItem': False, 'annualEvent': True, 'annualEventV2': True, 'availabilityStatusV2': {'display': 'In stock', 'value': 'IN_STOCK'}, 'groupMetaData': {'groupType': None, 'groupSubType': None, 'numberOfComponents': 0, 'groupComponents': None}, 'addOnServices': None, 'productLocation': None, 'fulfillmentSpeed': None, 'offerId': '2FCDF2944C6D3EADA4B9E5FAD09BF4AD', 'preOrder': {'isPreOrder': False, 'preOrderMessage': None, 'preOrderStreetDateMessage': None, 'streetDate': None, 'streetDateDisplayable': None, 'streetDateType': None, 'releaseDate': None}, 'pac': None, 'fulfillmentSummary': [{'fulfillment': 'DELIVERY', 'storeId': '0', 'deliveryDate': '2025-11-30T22:59:00.000Z', 'fulfillmentMethods': ['UNSCHEDULED'], 'fulfillmentBadge': None, 'outOfCountryEligible': None}], 'priceInfo': {'itemPrice': '$81.99', 'linePrice': 'Now $63.99', 'linePriceDisplay': 'Now $63.99', 'savings': 'SAVE $18.00', 'savingsAmt': 18, 'wasPrice': '$81.99', 'wasPriceSupportText': '', 'unitPrice': '', 'shipPrice': '', 'minPrice': 63.99, 'minPriceForVariant': '', 'priceRangeString': 'From $63.99', 'subscriptionPrice': '', 'subscriptionString': '', 'subscriptionDiscountPrice': '', 'priceDisplayCondition': '', 'finalCostByWeight': False, 'submapType': '', 'eaPricingText': '', 'eaPricingPreText': '', 'memberPriceString': '', 'subscriptionDualPrice': None, 'subscriptionPercentage': None, 'isB2BPrice': False, 'dutyFee': None, 'priceDisplayType': 'UNKNOWN'}, 'variantCriteria': [], 'snapEligible': False, 'fulfillmentTitle': 'title_shipToHome_not_available', 'fulfillmentType': 'FC', 'manufacturerName': None, 'showAtc': False, 'sponsoredProduct': {'spQs': 'SeMH-PkJWiXFR-ZKW5mTpJVn8OGalfRT7ah9IO3tAtGWDeo9Mh3V6Jh0pKP6wTfWkBGRo4103_13oSbIMEn90HoS3C_JTS1jYVXqMTiYjWQmxE3ohQdH22KRu2dWZf3Djxe0RnQevJAegAlbxKkngSm1R7VLeohaBO2AfSJNCRWtRc9m9efX5Jg57LJ0CPJDQ8Ww8RKl6OOtHWeqmpSMBF2GAozOuesv4pwNowaLjAo6WFgrtzu8BetnB1Zl_c6L', 'clickBeacon': 'https://www.walmart.com/sp/track?adUid=eee544b1-8532-462c-98aa-04a81760b543-0-0&pgId=tablet&spQs=SeMH-PkJWiXFR-ZKW5mTpJVn8OGalfRT7ah9IO3tAtGWDeo9Mh3V6Jh0pKP6wTfWkBGRo4103_13oSbIMEn90HoS3C_JTS1jYVXqMTiYjWQmxE3ohQdH22KRu2dWZf3Djxe0RnQevJAegAlbxKkngSm1R7VLeohaBO2AfSJNCRWtRc9m9efX5Jg57LJ0CPJDQ8Ww8RKl6OOtHWeqmpSMBF2GAozOuesv4pwNowaLjAo6WFgrtzu8BetnB1Zl_c6L&storeId=3081&pt=search&mloc=sp-search-middle&bkt=ace1_default%7Cace2_default%7Cace3_default%7Ccoldstart_on%7Csearch_default&pltfm=mweb&rdf=0&plmt=__plmt__&eventST=__eventST__&pos=__pos__&bt=__bt__&tn=WMT&wtn=elh9ie&tax=3944_1078524_1231200_5025899&spqc=qenv&et=head_torso&st=head', 'spTags': None, 'viewBeacon': None}, 'showOptions': True, 'showBuyNow': False, 'quickShop': None, 'quickShopCTALabel': None, 'rewards': None, 'promoData': [], 'promoDiscount': {'discount': 3, 'discountEligible': True, 'discountEligibleVariantPresent': False, 'promotionId': '1a7c7142-976c-468a-bb51-5a825dbf66de', 
'promoOffer': '1000161536', 'state': 'UNLOCK', 'showOtherEligibleItemsCTA': False, 'type': 'CONFIG_PROMO', 'min': 1, 'awardValue': 3, 'awardSubType': None, 'tiers': None}, 'arExperiences': {'isARHome': False, 'isZeekit': False, 'isAROptical': False}, 'eventAttributes': {'priceFlip': True, 'specialBuy': False}, 'subscription': {'__typename': 'SubscriptionData', 'subscriptionEligible': False, 'showSubscriptionCTA': False, 'subscriptionTransactable': False}, 'hasCarePlans': True, 'petRx': {'eligible': False, 'singleDispense': None}, 'vision': {'ageGroup': None, 'visionCenterApproved': False}, 'showExploreOtherConditionsCTA': False, 'isPreowned': False, 'pglsCondition': None, 'newConditionProductId': None, 'preownedCondition': None, 'keyAttributes': [{'displayEnum': 'other', 'value': '10.1 in'}], 
'mhmdFlag': False, 'seeSimilar': False, 'availabilityStatusDisplayValue': 'In stock', 'carrierDownpaymentPrice': '', 'productLocationDisplayValue': None, 'externalInfoUrl': '', 'canAddToCart': False, 'description': '', 'flag': 'Black Friday Deal', 'badge': {'__typename': 'BaseBadge', 'key': 'HOLIDAY_DEAL', 'text': 'Black Friday Deal', 'type': 'LABEL', 'id': 'L1800', 'styleId': 'PRIMARY_OZARKNOIR_BOLD'}, 'groupsV2': [{'name': 'flags', 'flow': 'HORIZONTAL', 'pos': 'ProdTileBadgeModule1', 'members': [{'memType': 'badge', 'memId': 'L1800', 'memStyleId': 'PRIMARY_MIDNIGHTBLUE', 'fbMemStyleId': None, 'content': [{'type': 'TEXT', 'value': 'Black Friday Deal', 'styleId': 'WHITE_BOLD', 'fbStyleId': None, 'contDesc': None, 'url': None, 'actionId': None}]}]}], 'swipeableImages': [], 'socialProofBadges': 
None, 'fulfillmentBadges': [], 'preOrderBadge': None, 'fulfillmentBadgeGroups': [{'text': 'Free shipping, arrives ', 'slaText': 'in 3+ days', 'isSlaTextBold': True, 'key': 'FF_SHIPPING', 'templates': None, 'textTemplate': None, 'textValues': None, 'sla': None, 'className': 'dark-gray'}], 'fulfillmentIcon': {'key': 'SAVE_WITH_W_PLUS', 'label': 'Save with'}, 'specialBuy': False, 'priceFlip': True, 'image': 'https://i5.walmartimages.com/seo/10-1-Inch-HD-Processor-Gray-Android-Tablet-10GB-RAM-64-GB-ROM-BT-5-0-Dual-Camera-Office-Tablet-Computer-Gray_c88cb895-2778-48bd-9ffd-223ae43c1477.6ed6753b90896ee7ceca1be9e89b1e6e.jpeg?odnHeight=180&odnWidth=180&odnBg=FFFFFF', 'imageSize': '', 'imageID': 'B9450E52DC054DB5957549ED91A2DD11', 'imageName': '10-1-Inch-HD-Processor-Gray-Android-Tablet-10GB-RAM-64-GB-': 'Now $63.99', 'savings': 'SAVE $18.00', 'savingsAmt': 18, 'wasPrice': '$81.99', 'wasPriceSupportText': '', 'unitPrice': '', 'shipPrice': '', 'minPrice': 63.99, 'minPriceForVariant': '', 'priceRangeString': 'From $63.99', 'subscriptionPrice': '', 'subscriptionString': '', 'subscriptionDiscountPrice': '', 'priceDisplayCondition': '', 'finalCostByWeight': False, 'submapType': '', 'eaPricingText': '', 'eaPricingPreText': '', 'memberPriceString': '', 'subscriptionDualPrice': None, 'subscriptionPercentage': None, 'isB2BPrice': False, 'dutyFee': None, 'priceDisplayType': 'UNKNOWN'}, 'variantCriteria': [], 'snapEligible': False, 'fulfillmentTitle': 'title_shipToHome_not_available', 'fulfillmentType': 'FC', 'manufacturerName': None, 'showAtc': False, 'sponsoredProduct': {'spQs': 'SeMH-PkJWiXFR-ZKW5mTpJVn8OGalfRT7ah9IO3tAtGWDeo9Mh3V6Jh0pKP6wTfWkBGRo4103_13oSbIMEn90HoS3C_JTS1jYVXqMTiYjWQmxE3ohQdH22KRu2dWZf3Djxe0RnQevJAegAlbxKkngSm1R7VLeohaBO2AfSJNCRWtRc9m9efX5Jg57LJ0CPJDQ8Ww8RKl6OOtHWeqmpSMBF2GAozOuesv4pwNowaLjAo6WFgrtzu8BetnB1Zl_c6L', 'clickBeacon': 'https://www.walmart.com/sp/track?adUid=eee544b1-8532-462c-98aa-04a81760b543-0-0&pgId=tablet&spQs=SeMH-PkJWiXFR-ZKW5mTpJVn8OGalfRT7ah9IO3tAtGWDeo9Mh3V6Jh0pKP6wTfWkBGRo4103_13oSbIMEn90HoS3C_JTS1jYVXqMTiYjWQmxE3ohQdH22KRu2dWZf3Djxe0RnQevJAegAlbxKkngSm1R7VLeohaBO2AfSJNCRWtRc9m9efX5Jg57LJ0CPJDQ8Ww8RKl6OOtHWeqmpSMBF2GAozOuesv4pwNowaLjAo6WFgrtzu8BetnB1Zl_c6L&storeId=3081&pt=search&mloc=sp-search-middle&bkt=ace1_default%7Cace2_default%7Cace3_default%7Ccoldstart_on%7Csearch_default&pltfm=mweb&rdf=0&plmt=__plmt__&eventST=__eventST__&pos=__pos__&bt=__bt__&tn=WMT&wtn=elh9ie&tax=3944_1078524_1231200_5025899&spqc=qenv&et=head_torso&st=head', 'spTags': None, 'viewBeacon': None}, 'showOptions': True, 'showBuyNow': False, 'quickShop': None, 'quickShopCTALabel': None, 'rewards': None, 'promoData': [], 'promoDiscount': {'discount': 3, 'discountEligible': True, 'discountEligibleVariantPresent': False, 'promotionId': '1a7c7142-976c-468a-bb51-5a825dbf66de', 
'promoOffer': '1000161536', 'state': 'UNLOCK', 'showOtherEligibleItemsCTA': False, 'type': 'CONFIG_PROMO', 'min': 1, 'awardValue': 3, 'awardSubType': None, 'tiers': None}, 'arExperiences': {'isARHome': False, 'isZeekit': False, 'isAROptical': False}, 'eventAttributes': {'priceFlip': True, 'specialBuy': False}, 'subscription': {'__typename': 'SubscriptionData', 'subscriptionEligible': False, 'showSubscriptionCTA': False, 'subscriptionTransactable': False}, 'hasCarePlans': True, 'petRx': {'eligible': False, 'singleDispense': None}, 'vision': {'ageGroup': None, 'visionCenterApproved': False}, 'showExploreOtherConditionsCTA': False, 'isPreowned': False, 'pglsCondition': None, 'newConditionProductId': None, 'preownedCondition': None, 'keyAttributes': [{'displayEnum': 'other', 'value': '10.1 in'}], 
'mhmdFlag': False, 'seeSimilar': False, 'availabilityStatusDisplayValue': 'In stock', 'carrierDownpaymentPrice': '', 'productLocationDisplayValue': None, 'externalInfoUrl': '', 'canAddToCart': False, 'description': '', 'flag': 'Black Friday Deal', 'badge': {'__typename': 'BaseBadge', 'key': 'HOLIDAY_DEAL', 'text': 'Black Friday Deal', 'type': 'LABEL', 'id': 'L1800', 'styleId': 'PRIMARY_OZARKNOIR_BOLD'}, 'groupsV2': [{'name': 'flags', 'flow': 'HORIZONTAL', 'pos': 'ProdTileBadgeModule1', 'members': [{'memType': 'badge', 'memId': 'L1800', 'memStyleId': 'PRIMARY_MIDNIGHTBLUE', 'fbMemStyleId': None, 'content': [{'type': 'TEXT', 'value': 'Black Friday Deal', 'styleId': 'WHITE_BOLD', 'fbStyleId': None, 'contDesc': None, 'url': None, 'actionId': None}]}]}], 'swipeableImages': [], 'socialProofBadges': 
None, 'fulfillmentBadges': [], 'preOrderBadge': None, 'fulfillmentBadgeGroups': [{'text': 'Free shipping, arrives ', 'slaText': 'in 3+ days', 'isSlaTextBold': True, 'key': 'FF_SHIPPING', 'templates': None, 'textTemplate': None, 'textValues': None, 'sla': None, 'className': 'dark-gray'}], 'fulfillmentIcon': {'key': 'SAVE_WITH_W_PLUS', 'label': 'Save with'}, 'specialBuy': False, 'priceFlip': True, 'image': 'https://i5.walmartimages.com/seo/10-1-Inch-HD-Processor-Gray-Android-Tablet-10GB-RAM-64-GB-ROM-BT-5-0-Dual-Camera-Office-Tablet-Computer-Gray_c88cb895-2778-48bd-9ffd-223ae43c1477.6ed6753b90896ee7ceca1be9e89b1e6e.jpeg?odnHeight=180&odnWidth=180&odnBg=FFFFFF', 'imageSize': '', 'imageID': 'B9450E52DC054DB5957549ED91A2DD11', 'imageName': '10-1-Inch-HD-Processor-Gray-Android-Tablet-10GB-RAM-64-GB-ROM-BT-5-0-Dual-Camera-Office-Tablet-Computer-Gray_c88cb895-2778-48bd-9ffd-223ae43c1477.6ed6753b90896ee7ceca1be9e89b1e6e.jpeg', 'isOutOfStock': False, 'price': 63.99, 'rating': {'averageRating': 4, 'nuTpJVn8OGalfRT7ah9IO3tAtGWDeo9Mh3V6Jh0pKP6wTfWkBGRo4103_13oSbIMEn90HoS3C_JTS1jYVXqMTiYjWQmxE3ohQdH22KRu2dWZf3Djxe0RnQevJAegAlbxKkngSm1R7VLeohaBO2AfSJNCRWtRc9m9efX5Jg57LJ0CPJDQ8Ww8RKl6OOtHWeqmpSMBF2GAozOuesv4pwNowaLjAo6WFgrtzu8BetnB1Zl_c6L', 'clickBeacon': 'https://www.walmart.com/sp/track?adUid=eee544b1-8532-462c-98aa-04a81760b543-0-0&pgId=tablet&spQs=SeMH-PkJWiXFR-ZKW5mTpJVn8OGalfRT7ah9IO3tAtGWDeo9Mh3V6Jh0pKP6wTfWkBGRo4103_13oSbIMEn90HoS3C_JTS1jYVXqMTiYjWQmxE3ohQdH22KRu2dWZf3Djxe0RnQevJAegAlbxKkngSm1R7VLeohaBO2AfSJNCRWtRc9m9efX5Jg57LJ0CPJDQ8Ww8RKl6OOtHWeqmpSMBF2GAozOuesv4pwNowaLjAo6WFgrtzu8BetnB1Zl_c6L&storeId=3081&pt=search&mloc=sp-search-middle&bkt=ace1_default%7Cace2_default%7Cace3_default%7Ccoldstart_on%7Csearch_default&pltfm=mweb&rdf=0&plmt=__plmt__&eventST=__eventST__&pos=__pos__&bt=__bt__&tn=WMT&wtn=elh9ie&tax=3944_1078524_1231200_5025899&spqc=qenv&et=head_torso&st=head', 'spTags': None, 'viewBeacon': None}, 'showOptions': True, 'showBuyNow': False, 'quickShop': None, 'quickShopCTALabel': None, 'rewards': None, 'promoData': [], 'promoDiscount': {'discount': 3, 'discountEligible': True, 'discountEligibleVariantPresent': False, 'promotionId': '1a7c7142-976c-468a-bb51-5a825dbf66de', 
'promoOffer': '1000161536', 'state': 'UNLOCK', 'showOtherEligibleItemsCTA': False, 'type': 'CONFIG_PROMO', 'min': 1, 'awardValue': 3, 'awardSubType': None, 'tiers': None}, 'arExperiences': {'isARHome': False, 'isZeekit': False, 'isAROptical': False}, 'eventAttributes': {'priceFlip': True, 'specialBuy': False}, 'subscription': {'__typename': 'SubscriptionData', 'subscriptionEligible': False, 'showSubscriptionCTA': False, 'subscriptionTransactable': False}, 'hasCarePlans': True, 'petRx': {'eligible': False, 'singleDispense': None}, 'vision': {'ageGroup': None, 'visionCenterApproved': False}, 'showExploreOtherConditionsCTA': False, 'isPreowned': False, 'pglsCondition': None, 'newConditionProductId': None, 'preownedCondition': None, 'keyAttributes': [{'displayEnum': 'other', 'value': '10.1 in'}], 
'mhmdFlag': False, 'seeSimilar': False, 'availabilityStatusDisplayValue': 'In stock', 'carrierDownpaymentPrice': '', 'productLocationDisplayValue': None, 'externalInfoUrl': '', 'canAddToCart': False, 'description': '', 'flag': 'Black Friday Deal', 'badge': {'__typename': 'BaseBadge', 'key': 'HOLIDAY_DEAL', 'text': 'Black Friday Deal', 'type': 'LABEL', 'id': 'L1800', 'styleId': 'PRIMARY_OZARKNOIR_BOLD'}, 'groupsV2': [{'name': 'flags', 'flow': 'HORIZONTAL', 'pos': 'ProdTileBadgeModule1', 'members': [{'memType': 'badge', 'memId': 'L1800', 'memStyleId': 'PRIMARY_MIDNIGHTBLUE', 'fbMemStyleId': None, 'content': [{'type': 'TEXT', 'value': 'Black Friday Deal', 'styleId': 'WHITE_BOLD', 'fbStyleId': None, 'contDesc': None, 'url': None, 'actionId': None}]}]}], 'swipeableImages': [], 'socialProofBadges': 
None, 'fulfillmentBadges': [], 'preOrderBadge': None, 'fulfillmentBadgeGroups': [{'text': 'Free shipping, arrives ', 'slaText': 'in 3+ days', 'isSlaTextBold': True, 'key': 'FF_SHIPPING', 'templates': None, 'textTemplate': None, 'textValues': None, 'sla': None, 'className': 'dark-gray'}], 'fulfillmentIcon': {'key': 'SAVE_WITH_W_PLUS', 'label': 'Save with'}, 'specialBuy': False, 'priceFlip': True, 'image': 'https://i5.walmartimages.com/seo/10-1-Inch-HD-Processor-Gray-Android-Tablet-10GB-RAM-64-GB-ROM-BT-5-0-Dual-Camera-Office-Tablet-Computer-Gray_c88cb895-2778-48bd-9ffd-223ae43c1477.6ed6753b90896ee7ceca1be9e89b1e6e.jpeg?odnHeight=180&odnWidth=180&odnBg=FFFFFF', 'imageSize': '', 'imageID': 'B9450E52DC054DB5957549ED91A2DD11', 'imageName': '10-1-Inch-HD-Processor-Gray-Android-Tablet-10GB-RAM-64-GB-ROM-BT-5-0-Dual-Camera-Office-Tablet-Computer-Gray_c88cb895-2778-48bd-9ffd-223ae43c1477.6ed6753b90896ee7ceca1be9e89b1e6e.jpeg', 'isOutOfStock': False, 'price': 63.99, 'rating': {'averageRating': 4, 'nu False, 'isZeekit': False, 'isAROptical': False}, 'eventAttributes': {'priceFlip': True, 'specialBuy': False}, 'subscription': {'__typename': 'SubscriptionData', 'subscriptionEligible': False, 'showSubscriptionCTA': False, 'subscriptionTransactable': False}, 'hasCarePlans': True, 'petRx': {'eligible': False, 'singleDispense': None}, 'vision': {'ageGroup': None, 'visionCenterApproved': False}, 'showExploreOtherConditionsCTA': False, 'isPreowned': False, 'pglsCondition': None, 'newConditionProductId': None, 'preownedCondition': None, 'keyAttributes': [{'displayEnum': 'other', 'value': '10.1 in'}], 
'mhmdFlag': False, 'seeSimilar': False, 'availabilityStatusDisplayValue': 'In stock', 'carrierDownpaymentPrice': '', 'productLocationDisplayValue': None, 'externalInfoUrl': '', 'canAddToCart': False, 'description': '', 'flag': 'Black Friday Deal', 'badge': {'__typename': 'BaseBadge', 'key': 'HOLIDAY_DEAL', 'text': 'Black Friday Deal', 'type': 'LABEL', 'id': 'L1800', 'styleId': 'PRIMARY_OZARKNOIR_BOLD'}, 'groupsV2': [{'name': 'flags', 'flow': 'HORIZONTAL', 'pos': 'ProdTileBadgeModule1', 'members': [{'memType': 'badge', 'memId': 'L1800', 'memStyleId': 'PRIMARY_MIDNIGHTBLUE', 'fbMemStyleId': None, 'content': [{'type': 'TEXT', 'value': 'Black Friday Deal', 'styleId': 'WHITE_BOLD', 'fbStyleId': None, 'contDesc': None, 'url': None, 'actionId': None}]}]}], 'swipeableImages': [], 'socialProofBadges': 
None, 'fulfillmentBadges': [], 'preOrderBadge': None, 'fulfillmentBadgeGroups': [{'text': 'Free shipping, arrives ', 'slaText': 'in 3+ days', 'isSlaTextBold': True, 'key': 'FF_SHIPPING', 'templates': None, 'textTemplate': None, 'textValues': None, 'sla': None, 'className': 'dark-gray'}], 'fulfillmentIcon': {'key': 'SAVE_WITH_W_PLUS', 'label': 'Save with'}, 'specialBuy': False, 'priceFlip': True, 'image': 'https://i5.walmartimages.com/seo/10-1-Inch-HD-Processor-Gray-Android-Tablet-10GB-RAM-64-GB-ROM-BT-5-0-Dual-Camera-Office-Tablet-Computer-Gray_c88cb895-2778-48bd-9ffd-223ae43c1477.6ed6753b90896ee7ceca1be9e89b1e6e.jpeg?odnHeight=180&odnWidth=180&odnBg=FFFFFF', 'imageSize': '', 'imageID': 'B9450E52DC054DB5957549ED91A2DD11', 'imageName': '10-1-Inch-HD-Processor-Gray-Android-Tablet-10GB-RAM-64-GB-ROM-BT-5-0-Dual-Camera-Office-Tablet-Computer-Gray_c88cb895-2778-48bd-9ffd-223ae43c1477.6ed6753b90896ee7ceca1be9e89b1e6e.jpeg', 'isOutOfStock': False, 'price': 63.99, 'rating': {'averageRating': 4, 'nuD'}, 'groupsV2': [{'name': 'flags', 'flow': 'HORIZONTAL', 'pos': 'ProdTileBadgeModule1', 'members': [{'memType': 'badge', 'memId': 'L1800', 'memStyleId': 'PRIMARY_MIDNIGHTBLUE', 'fbMemStyleId': None, 'content': [{'type': 'TEXT', 'value': 'Black Friday Deal', 'styleId': 'WHITE_BOLD', 'fbStyleId': None, 'contDesc': None, 'url': None, 'actionId': None}]}]}], 'swipeableImages': [], 'socialProofBadges': 
None, 'fulfillmentBadges': [], 'preOrderBadge': None, 'fulfillmentBadgeGroups': [{'text': 'Free shipping, arrives ', 'slaText': 'in 3+ days', 'isSlaTextBold': True, 'key': 'FF_SHIPPING', 'templates': None, 'textTemplate': None, 'textValues': None, 'sla': None, 'className': 'dark-gray'}], 'fulfillmentIcon': {'key': 'SAVE_WITH_W_PLUS', 'label': 'Save with'}, 'specialBuy': False, 'priceFlip': True, 'image': 'https://i5.walmartimages.com/seo/10-1-Inch-HD-Processor-Gray-Android-Tablet-10GB-RAM-64-GB-ROM-BT-5-0-Dual-Camera-Office-Tablet-Computer-Gray_c88cb895-2778-48bd-9ffd-223ae43c1477.6ed6753b90896ee7ceca1be9e89b1e6e.jpeg?odnHeight=180&odnWidth=180&odnBg=FFFFFF', 'imageSize': '', 'imageID': 'B9450E52DC054DB5957549ED91A2DD11', 'imageName': '10-1-Inch-HD-Processor-Gray-Android-Tablet-10GB-RAM-64-GB-ROM-BT-5-0-Dual-Camera-Office-Tablet-Computer-Gray_c88cb895-2778-48bd-9ffd-223ae43c1477.6ed6753b90896ee7ceca1be9e89b1e6e.jpeg', 'isOutOfStock': False, 'price': 63.99, 'rating': {'averageRating': 4, 'nuone, 'textTemplate': None, 'textValues': None, 'sla': None, 'className': 'dark-gray'}], 'fulfillmentIcon': {'key': 'SAVE_WITH_W_PLUS', 'label': 'Save with'}, 'specialBuy': False, 'priceFlip': True, 'image': 'https://i5.walmartimages.com/seo/10-1-Inch-HD-Processor-Gray-Android-Tablet-10GB-RAM-64-GB-ROM-BT-5-0-Dual-Camera-Office-Tablet-Computer-Gray_c88cb895-2778-48bd-9ffd-223ae43c1477.6ed6753b90896ee7ceca1be9e89b1e6e.jpeg?odnHeight=180&odnWidth=180&odnBg=FFFFFF', 'imageSize': '', 'imageID': 'B9450E52DC054DB5957549ED91A2DD11', 'imageName': '10-1-Inch-HD-Processor-Gray-Android-Tablet-10GB-RAM-64-GB-ROM-BT-5-0-Dual-Camera-Office-Tablet-Computer-Gray_c88cb895-2778-48bd-9ffd-223ae43c1477.6ed6753b90896ee7ceca1be9e89b1e6e.jpeg', 'isOutOfStock': False, 'price': 63.99, 'rating': {'averageRating': 4, 'nu7ceca1be9e89b1e6e.jpeg?odnHeight=180&odnWidth=180&odnBg=FFFFFF', 'imageSize': '', 'imageID': 'B9450E52DC054DB5957549ED91A2DD11', 'imageName': '10-1-Inch-HD-Processor-Gray-Android-Tablet-10GB-RAM-64-GB-ROM-BT-5-0-Dual-Camera-Office-Tablet-Computer-Gray_c88cb895-2778-48bd-9ffd-223ae43c1477.6ed6753b90896ee7ceca1be9e89b1e6e.jpeg', 'isOutOfStock': False, 'price': 63.99, 'rating': {'averageRating': 4, 'nuROM-BT-5-0-Dual-Camera-Office-Tablet-Computer-Gray_c88cb895-2778-48bd-9ffd-223ae43c1477.6ed6753b90896ee7ceca1be9e89b1e6e.jpeg', 'isOutOfStock': False, 'price': 63.99, 'rating': {'averageRating': 4, 'numberOfReviews': 274}, 'salesUnit': 'EACH', 'variantList': [], 'isVariantTypeSwatch': False, 'shouldLazyLoad': False, 'isSponsoredFlag': True, 'moqText': None, 'isLeftSideGridItem': False, 'productAttributes': {}, 'productIndex': 0, 'itemStackPosition': 1, 'modularStackKey': 'eee544b1-8532-462c-98aa-04a81760b543-0-0'}
        """
        
        for product_data in grouped_products['items']:   ## grouped products is a dict with key item contain all data
            try:
                product_info = {
                    'DateCheck':DateCheck,
                    'Market':'Walmart',
                    'product_id':product_data['id'],
                    'product_name':product_data['name'],
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
                    'Img_src':product_data['imageInfo']['thumbnailUrl'],
                    'Link': 'https://www.walmart.com/' + product_data['canonicalUrl'],

                }
            except: 
                print('walmart error')
            else : 
                whole_products_info.append(product_info)
    # else : print("Walmart empty page")
    # print(whole_products_info)
    info_into_df(whole_products_info)


### Amazon Main search function for every page
def amazon_page_search(search_name,page):
    url = 'https://www.amazon.eg/s?k=' + search_name + '&page=' + str(page)
    wd.get(url)
    time.sleep(3)
    all_products = wd.find_elements(By.CSS_SELECTOR,"div[role='listitem']")
    products_data = []
    if len(all_products) != 0:
        # print(len(all_products))
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
                    try : img = product.find_element(By.TAG_NAME,"img").get_attribute('src')
                    except:img=None
        # great exception code to view the errorType
            # except Exception as ex:
            #     template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            #     message = template.format(type(ex).__name__, ex.args)
            #     print(message)
            except :
                print('amazon, some data not available of product')
            else :
                price = str(product_price) + str(product_currency)
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
                # product_info = [DateCheck,Market,product_asin,product_name,price,product_rating,str(link_to_product)]
                products_data.append(product_info)
        # print(products_data)
        info_into_df(products_data)
    else : print('amazon empty page')




search_name = 'laptops'
page = 1   


## Loop for continous scraping for first 10 pages
while True:
    ##################### Good working interval 3min and good order for webs to avoid get panned from scraping  #####################
    time.sleep(120)
    amazon_page_search(search_name,page)
    alibaba_page_search(search_name,page)
    ebay_page_search(search_name,page)
    walmart_page_search(search_name,page)
    # break
    time.sleep(10)
    
    page+=1
    if page > 5:
        create_excel()
        wd.quit()
        break





## failed
# # scheduling same code to run multiple
# # times after every 1 minute 

# def job():
#     print('activating')
#     print(page)
#     alibaba_page_search(search_name,page)
#     ebay_page_search(search_name,page)
#     walmart_page_search(search_name,page)
#     amazon_page_search(search_name,page)
#     page+=1


# schedule.every(3).minutes.do(job)

# while True:
#     # running all pending tasks/jobs
#     time.sleep(30) 
#     schedule.run_pending()
#     if page > 3:
#         create_excel()
#         wd.quit()
#         break
    






















"""
### Walmart search each product page
def extract_product_data(product_url):
    response = requests.get(product_url,headers=headers)
    soup = BeautifulSoup(response.text,'html.parser')
    next_data = soup.find('script',id='__NEXT_DATA__')

    # print(data['props']['pageProps']['initialData']['data']['product']['priceInfo']['currentPrice'].keys())
    # print(data['props']['pageProps']['initialData']['data']['product']['priceInfo']['currentPrice']['price'])  ## working

    ## 2 dict down displaying paths for most valuable elements for product
    data = json.loads(next_data.string)
    # initial_data = data['props']['pageProps']['initialData']
    if 'initialData' in list(data['props']['pageProps'].keys()) :
        if 'data' in list(data['props']['pageProps']['initialData'].keys()):
            try:
                product_data = data['props']['pageProps']['initialData']['data']
                product_info={
                    "DateCheck": DateCheck,
                    "product_id":product_data['product']['id'],
                    'product_name': product_data['product']['name'],
                    'price': product_data['product']['priceInfo']['currentPrice'][ 'price'],
                    'Rating':product_data['product']['averageRating'],
                    # 'brand': product_data[ 'product']['brand'],
                    'Link':product_data[ 'product']['canonicalUrl'],
                    # 'savings_percent': product_data['product'] ['priceInfo']['savings']['percent']
                }
            except:print('some data are missing')
            else:
                product_info['Link'] = 'https://www.walmart.com/' + product_info['Link']
                return product_info
### loop for every product page
def search_walmart_products(page_urls):
    products_one_page = page_urls

    for product_url in products_one_page:
        product_info = extract_product_data(product_url)
        print(product_info)

        if product_info : ## to not call the function if return nonetype when link has no data
            info_into_df(product_info)
    

            
            """


