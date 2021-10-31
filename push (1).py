import requests as req
import pandas as pd
from bs4 import BeautifulSoup
import time
import re
import io
import random
from random import randint
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64 x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}

'''Function to get the URL of a perfume
and then iterating with the URL'''

df1 = pd.DataFrame()
productlinks = []
with open('C:/Users/usury/AppData/Local/Programs/Python/Python38-32/list2.txt', 'r') as file:
    for line in file:
        h = line
productlinks = h.split()

iter = 0
for iter in range(0,163):
  df3 = pd.DataFrame()
  print(iter)
  '''Reading the page'''
  time.sleep(random.randint(60,80))
  try:
    r3 = req.get(productlinks[iter], headers=headers)
    print(r3)
  except:
    continue
  if str(r3) != "<Response [200]>":
    break

  '''time.sleep(random.randint(0,1))'''
  soup3 = BeautifulSoup(r3.content, 'lxml')

  '''Finding the index of the page'''
  index1 = re.findall(r'\d+', productlinks[iter]) 
    
  '''Finding perfume brand name'''
  try:
      pname = ''
      pname = soup3.find('h1', itemprop='name').text.strip()
      '''time.sleep(random.randint(0,3))'''
      
  except:
      pname = None
  try:
      brand = ''
      brand = soup3.find('span', itemprop='name').text.strip()
      '''time.sleep(random.randint(0,3))'''
  except:
      brand = None

  '''Finding the ratings'''
  try:
    rating =''
    rating = soup3.find('span', itemprop="ratingValue").text.strip()
    '''time.sleep(random.randint(0,5))'''
  except:
    rating = None

  '''Getting the date and time of the review'''
  a=''
  a=soup3.find_all('span',class_="vote-button-legend")
  '''time.sleep(random.randint(0,3))'''
  date=[]
  for ia in a:
    date.append(ia.text.strip())
  mainaccord = ''
  mainaccord = soup3.find_all('div', class_="accord-bar")
  '''time.sleep(random.randint(0,3))'''
  accordlist=[]
  if mainaccord!='':
    for accord in mainaccord:
        '''time.sleep(2)'''
        '''Getting the main accords'''
        accordlist.append(accord.text.strip())
        '''Unpacking the accord list; eliminating the list format'''
        accordlist_main = ', '.join(accordlist)
  else:
    accordlist_main = None

  longevity_list = ''
  longevity_list = soup3.find_all('div', class_="cell small-12 medium-6")
  '''time.sleep(random.randint(0,3))'''
  try:
    longevity = longevity_list[1].text.strip()[19:23]
  except:
    longevity = None
  try: 
    sillage = longevity_list[2].text.strip()[17:21]
  except:
    sillage = None

  '''Getting perfumer name
  perf_name=None
  time.sleep(random.randint(0,3))
  perfumerlist = soup3.find_all('div', class_="grid-x grid-padding-x grid-padding-y small-up-2 medium-up-2")
  for pername in perfumerlist:
      perf_name = pername.find('a').text.strip()'''

  try:
    '''Finding the price'''
    pric = ''
    pric = soup3.find_all('div',class_="cell small-12 medium-6 text-center")
    for ip in pric:
      USD=str(ip.find('a'))
      if len(re.findall("USD",USD)) != 0:
        price = ip.find('a').find('b').text.strip()
      else:
        price = None
    '''time.sleep(random.randint(0,3))'''
  except:
    price = None


  '''Finding launch year from description'''
  try:
    year=''
    description_data = soup3.find('div', itemprop="description").text.strip()
    '''finding first digit with 1/2 and next 3 between 0-9 for launch year'''
    year = re.findall("([1-2][0-9]{3})",str(description_data))[0]
  except:
    year = None

  '''Icon vote information'''
  Vote_List = ['rating', 'winter', 'spring', 'summer', 'autumn', 'day', 'night', 'longevity', 'sillage', 'gender',
                'relation']


  olist=[]
  '''time.sleep(random.randint(0,3))'''
  s1=''
  s1 = soup3.find_all("div", class_="cell fragrance-review-box",itemtype="http://schema.org/Review")
  for s2 in s1:
      rows = str(s2.find('user-perfume-votes'))
      votei = []
      try:
          for vote in Vote_List:
              index = rows.find(vote)
              n = index + len(vote) + 20
              partitioned_string = rows[index:n]
              votei.append(re.split(':|,|}', partitioned_string)[1].strip('"'))
      except:
              for f in range(11):
                  votei.append(None)
      olist.append(votei)


  '''Getting the perfume ddescription box'''
  try:
    description_data = ''
    description_data = soup3.find('div', itemprop="description").text.strip()
  except:
    description_data = ''
  '''time.sleep(random.randint(0,3))'''

  '''Fetching the index of the keywords:topnotes,middlenotes and basenotes'''
  top_Index = ''
  middle_Index = ''
  base_Index = ''
  try:
      top_Index = (description_data.index('Top note'))
      top_Notes= description_data[top_Index::]
      top_Notes1 = str(top_Notes).split(';')[0]
      topN=re.split(',|;| is | are | and',top_Notes1)
      TNote=topN[1:]
  except:
    TNote=''

  try:
      middle_Index = description_data.index('middle note')
      if middle_Index == '':
        middle_Index = description_data.index('heart note')
      middle_Notes= description_data[middle_Index::]
      middle_Notes1 = str(middle_Notes).split(';')[0]
      middleN=re.split(',|;| is|are | and',middle_Notes1)
      MNote=middleN[1:len(middleN):]
  except:
      MNote=''

  try:
    base_Index = description_data.index('base note')
    if base_Index == '':
      base_Index = description_data.index('bottom note')
    '''Splitting the contents into desired strings'''
    base_N= description_data[base_Index::]
    base_Notes=base_N[0:base_N.index('.'):]

    '''Extracting only the required words'''
    baseN=re.split(',| is|are | and',base_Notes)
    BNote=baseN[1:len(baseN):]

  except:
    BNote=''
     
      

  '''Getting perfumer name'''
  perfname=[]
  try:
    perfumerlist=''
    perfumerlist = soup3.find('div', class_="grid-x grid-padding-x grid-padding-y small-up-2 medium-up-2").text.strip()
    if len(perfumerlist)!=0:
      per = perfumerlist.split("\n")
      for i1 in per:
        if i1 !="":
          perfname.append(i1)
  except:
    if len(perfumerlist)!=0:
      per = perfumerlist.split("\n")
      for i1 in per:
        if i1 !="":
          perfname.append(i1)
    else:
      try:
        perfumerlist = soup3.find('div', class_="grid-x grid-padding-x grid-padding-y small-up-2 medium-up-4").text.strip()
        per = perfumerlist.split("\n")
        print(len(per))
        for i1 in per:
          if i1 !="":
            perfname.append(i1)
      except:
        perfname = ''


  '''writing into the pandas df'''

  k = 0
  m = 0
  '''Finding the reviews'''
  try:
    review = ''
    review = soup3.find_all('div', itemprop="reviewBody")
  except:
    review = None
  '''reviewer name'''
  try:
    reviewer_data = ''
    reviewer_data = soup3.find_all('b', class_="idLinkify")
  except:
    reviewer_data = None
  '''time and date of the review'''
  try:
    review_date = ''
    review_date=soup3.find_all('span', class_="vote-button-legend")
  except:
    review_date = None

 
  for rev in review:
      df2 = pd.DataFrame({'Pcode':[''.join(index1)],'Perfume_Name': [pname], 'Reviewer Name': [reviewer_data[k].text.strip()],
        'Review_Date': [review_date[k].text.strip()], 'Rating(max:5)' :[olist[m][0]], 'Winter' :[olist[m][1]], 'Spring' :[olist[m][2]],
        'Summer' :[olist[m][3]], 'Autumn' :[olist[m][4]], 'Day' :[olist[m][5]], 'Night' :[olist[m][6]],
        'Longevity' :[olist[m][7]], 'Sillage':[olist[m][8]], 'Gender':[olist[m][9]],
        'Relation':[olist[m][10]], 'Reviews': [rev.text.strip()]})

      k += 1
      m += 1
      df3 = df3.append(df2, ignore_index=True)
  df3.to_csv('Brazil_Fragrantica_reviews.csv',mode='a', header=False,index=False)
  df100 = pd.DataFrame({'Pcode':[''.join(index1)],'Perfume_Name': [pname], 'Perfume_Link': [productlinks[iter]],'Brand': [brand],'Perfumer_Name' : [', '.join(perfname)],'Price in USD':[price], 'Rating(max:5)': [rating], 'Launch Year':[year],
                          'MainAccords': [accordlist_main],'Top Notes':[', '.join(TNote)],'Middle Notes':[', '.join(MNote)], 'Base Notes':[', '.join(BNote)], 'Longevity(max:5)': [longevity], 'Sillage(max:4)': [sillage]})
  

  df1 = df1.append(df100,ignore_index=True)

df1.to_csv('Brazil_Fragrantica_searchpage_info.csv',mode='a', header=False,index=False)

