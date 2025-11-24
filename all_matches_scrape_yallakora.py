from bs4 import BeautifulSoup
import requests
from lxml import html
import pandas as pd
import numpy as np
import time


import datetime
today_date = (datetime.datetime.now().date()).strftime('%m/%d/%Y')
# print(today_date)



columns = ['MatchDay',"league_name","teamA",'score','teamB','pen']
Leagues_df = pd.DataFrame(columns=columns)


def create_excel():
    Leagues_df.to_excel('Yalla_coraMatches_since_2025_started.xlsx',index=False)


def check_leagues(day_box):
    leagues_boxes = day_box.find_all("div",attrs={'class':'matchCard'})
    return leagues_boxes

def search(url):
    # print(url)
    headers = {
    'sec-ch-ua-platform':"Android",
    'sec-fetch-dest':'empty',
    'sec-fetch-mode':'cors',
    'sec-fetch-site':'cross-site',
    'sec-fetch-storage-access':'active',
    'user-agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36 Edg/142.0.0.0'
    }
    # print(url)

    page = requests.get(url,headers=headers)
    soup = BeautifulSoup(page.content,'html.parser')

    # check if day_box that contains all leagues is present
    if soup.find("div",attrs={'id':'day'}):
        day_box = soup.find("div",attrs={'id':'day'})
        ## check league and team before processing:
        # if check_league(day_box):
        check_leagues(day_box)
        leagues_boxes = day_box.find_all("div",attrs={'class':'matchCard'})
        for leage in leagues_boxes :
            leage_name =leage.select("h2")[0].text.strip() ## in list form
            # print(leage_name)
            teams_boxes = leage.select("div.teamCntnr div.teamsData")
            for team_box in teams_boxes :
                teamA = team_box.select("div.teamA p")[0].text.strip()
                teamB = team_box.select("div.teamB p")[0].text.strip()
                result = team_box.select("div.MResult span") ## list of four items scoreA - scoreB
                pen = ''
                if len(result) == 4:
                    [scoreA,dash,scoreB,MTime] = [x.text.strip() for x in result]
                elif len(result) == 5:
                    [scoreA,dash,scoreB,MTime,pen] = [x.text.strip() for x in result]
                score = f'{scoreA} - {scoreB}'

                MatchData = [date,leage_name,teamA,score,teamB,pen]
                Leagues_df.loc[len(Leagues_df)] = MatchData
                # print(Leagues_df)

            # team = league_box.find('p',string=f'{team_name}')
            # if team :
            #     team_box = team.find_parent('div')
            #     match_box = team_box.find_parent('div')
            #     teamA = match_box.select('div:nth-child(1) > p')[0].text  # select >> returns a list
            #     teamB = match_box.select('div:nth-child(3) > p')[0].text  # select >> returns a list
            #     result = match_box.select('div:nth-child(2) > span')
            #     [scoreA,dash,scoreB,time] = [x.text for x in result]
            #     score = f'{scoreA}-{scoreB}'
            #     print(scoreA,dash,scoreB,time)
            #     match_data = [date,league_name,teamA,score,teamB]

            #     ## add match data to df
            #     teamMatches.loc[len(teamMatches)] = match_data
                # print(teamMatches)
            # else: print(f"NO matches for ur team at this day")
        # else: print(f"NO matches for this league at date : {date}")
    else:print('No matches at this day')
        




# team_name = input('Please enter team name to search: ').strip().lower()
# team_name = 'الأهلي'
# league_id = input('Please enter league id to search: ').strip().lower()
# league_name= 'دوري أبطال إفريقيا'
# enter_date = input('Please enter date to search: (eg : 11/22/2025 ) \n').strip().lower()
# enter_date = today_date
start_date = '01/01/2025'

# url_to_search = 'https://www.yallakora.com/match-center?date=' + f"{start_date}"
# search(url_to_search)

date = start_date
while True:
    print(date)
    ## make a loop to search for team and league in months
    url_to_search = 'https://www.yallakora.com/match-center?date=' + f"{date}"
    search(url_to_search)
    date_format = datetime.datetime.strptime(date,"%m/%d/%Y").date()
    date_format += datetime.timedelta(days=1)
    date = date_format.strftime('%m/%d/%Y')
    time.sleep(1)
    ## make a breakpoint
    if date == today_date : 
        create_excel()
        break

# import datetime

# date = "11/22/2022"
# now = datetime.datetime.strptime(date,"%m/%d/%Y").date()
# print(now)

# now += datetime.timedelta(days=1)

# print(now)