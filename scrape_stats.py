import time
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import calendar

# Google email
usernameStr = 'xxx'

# password
passwordStr = 'xxx'

# initialize Selenium webdriver
browser = webdriver.Chrome()

# open new tab with link to sign-in options for Medium
browser.get('https://medium.com/m/signin?redirect=https%3A%2F%2Fmedium.com%2F&operation=login')

# this pauses/delays the code execution for () seconds;
# very important - give time for page to load before searching out elements
# adjust (increase/decrease) depending on internet speed?
time.sleep(5)

# link to sign-in with Google - the 1st button on the page
browser.find_element_by_xpath('//button[1]').click()

time.sleep(2)

# enter your Google email
browser.find_element_by_id('identifierId').send_keys(usernameStr)

# click the "Next" button
browser.find_element_by_id('identifierNext').click()

time.sleep(2)

# enter your account password
browser.find_element_by_xpath("//input[@name='password'][@type='password']").send_keys(passwordStr)

# sign-in to your Medium account with Google auth!
browser.find_element_by_id('passwordNext').click()

time.sleep(5)

# go to stats page - you are now logged in to your Medium account
browser.get('https://medium.com/me/stats')

time.sleep(2)

# number of months to get stats for - adjust as you please
months = 10

viewstats = []     # number of views
readstats = []     # number of reads
i = 0
while i < months:
    # default data is on views
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    viewstats.append(soup.find_all('rect'))
    
    # get stats on article reads as well - this will be in reverse order from views
    # line below clicks on the "Reads" tab on the page - graph now shows read history
    browser.find_element_by_xpath("//li[@data-action='switch-graph'][@data-action-value='reads']").click()
    time.sleep(2)
    
    # parse page, and get data
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    readstats.append(soup.find_all('rect'))
    
    # increase counter
    i += 1
    
    # go to previous month
    browser.find_element_by_xpath("//button[@data-action='show-graph-previous']").click()
    time.sleep(2)
    
    # switch back to views
    browser.find_element_by_xpath("//li[@data-action='switch-graph'][@data-action-value='views']").click()
    time.sleep(2)
    
# close the webdriver (Chrome window)
browser.close()

# compile the data
statInfo = []

# for each 30-day period...
for j in range(len(viewstats)):
    # for each day in a selected 30-day period...
    for k in range(len(viewstats[j])):
        # add the year to the view date - 2019 if January, 2018 otherwise
        # not robust enough, but does the trick here...
        # and also get number of views
        # put both in a list, and append to array
        viewDate = viewstats[j][k]['data-tooltip'].split('on')[-1].strip()
        if viewDate.split('\xa0')[0].strip() == 'January':
            viewDate = viewDate + ' 2019'
        else:
            viewDate = viewDate + ' 2018'
        numViews = int(viewstats[j][k]['data-tooltip'].split(' ')[0])
        numReads = int(readstats[j][k]['data-tooltip'].split(' ')[0])
        statInfo.append([viewDate, numViews, numReads])
        
# dataframe to store the number of views for the article each day
statData = pd.DataFrame(statInfo, columns=['date', 'numberOfViews', 'numberOfReads'])

# create a string showing the full day and convert to datetime (Python time format)
statData['newDate'] = statData['date'].map(lambda x: x.split('\xa0')[0].strip() + '\\' + x.split('\xa0')[1].split(' ')[0].strip()+ '\\' + x.split('\xa0')[1].split(' ')[1].strip())
statData['newDate'] = statData['newDate'].map(lambda x: datetime.datetime.strptime(x, '%B\\%d\\%Y'))
statData['Weekday'] = statData.newDate.map(lambda x: calendar.day_name[x.weekday()])

# re-order by the date
statData.sort_values(by='newDate', inplace=True)

# rename columns, drop redundant columns, and re-order columns
statData.columns = ['oldDate', 'Views', 'Reads', 'Date', 'Weekday']
statData.reset_index(inplace=True)
statData.drop(labels=['oldDate', 'index'], axis=1, inplace=True)
statData = statData[['Date', 'Weekday', 'Views', 'Reads']]

# save to Excel if you want
statData.to_excel(pd.ExcelWriter('medium_stats.xlsx'),'Stats', index=False)