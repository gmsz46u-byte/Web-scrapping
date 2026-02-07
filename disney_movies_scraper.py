from bs4 import BeautifulSoup
import requests
import pandas as pd


### setting df
columns =['Release date','Title','Notes']
df = pd.DataFrame(columns=columns)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Edge-Cache-Control': 'no-cache',
    'X-Custom-Edge-Header': 'my-edge-value'
}    
url = 'https://en.wikipedia.org/wiki/List_of_Walt_Disney_Pictures_films'
response = requests.get(url=url,headers=headers)
soup = BeautifulSoup(response.content,'html.parser')

target_heads = soup.select("h3")[:9]
target_tables = soup.find_all('table')[:9]

target_block = []
for i in range (len(target_heads)) :
    target_block.append(target_heads[i])
    target_block.append(target_tables[i])

for el in target_block :
    if ((target_block.index(el)+1)%2) == 1 : ## for even indexes starting with zero representing h3 elements
        df.loc[len(df)] = el.get_text()

    else :                                    ## for odd indexes starting with 1 representing table elements
        trows = el.find_all("tr") 
        for row in trows :  ## trow = ['Release date\n', '\n' , 'Title\n', '\n' , 'Notes\n']
            row = list(filter((lambda x : x!= '\n'),[(td.get_text())for td in row]))  ### after filter method , still some rows have empty texts
            try: rel_date = row[0].strip("\n")
            except : rel_date = ''
            try: title = row[1].strip("\n")
            except : title = ''
            try: note = row[2].strip("\n")
            except : note = ''
            df.loc[len(df)] = [rel_date,title,note]

print(df)

df.to_csv('disney_movies.csv',index=False)
