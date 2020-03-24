import sys
from selenium import webdriver
from selenium.webdriver import PhantomJS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas_datareader.data as web 
import os
import requests
import bs4 as bs
from bs4 import BeautifulSoup
import datetime as dt 
import pickle
import sys
import tqdm
import warnings
warnings.filterwarnings("ignore")


#########################################################

start = dt.datetime(2008,1,1)
end = (dt.datetime.now()).strftime('%Y-%m-%d')
rsi_period = 14 #days

#########################################################

dfs = list()

print('>>>Updating Stock List')
# Scraping each page in website with list of stocks in B3

df = pd.DataFrame()

# Scraping site with list of stocks in B3
for page in range (1,5):
    
    #Exception treatment in case website reading goes wrong
    try:
        dfs = pd.read_html(f'https://www.guiainvest.com.br/lista-acoes/default.aspx?listaacaopage={page}', index_col = False )
    except Exception as e:
        if str(e) == '<urlopen error [Errno 11001] getaddrinfo failed>':
            print('\n Error accessing website, check internet connection')
            sys.exit(1)            
        else:
            raise
    
    #If dataframe is empty, it becomes the first dataframe fetched
    if df.empty:
        df = dfs[0]
    
    #Else, it will append the fetched dataframe from the website to current dataframe
    else:
        df = df.append(dfs[0])

# Droping useless columns with companies activity and unnamed
df.drop(['Unnamed: 0','Atividade Principal'], inplace=True, axis=1)

# Renaming columns with PT-BR writing
df.rename(columns={'CÃ³digo':'ticker','Nome de PregÃ£o':'Company'}, inplace=True)

# Setting tickers as index to locate problematic rows
df.set_index('ticker', inplace=True)

# Copying dataframe into a new one
B3_tickers = df.copy()

# Droping that last NaN
B3_tickers.dropna(inplace=True)

# Droping unwanted rows
for ticker in B3_tickers.index:
    if len(ticker) > 6:
        B3_tickers.drop(ticker, inplace=True)


#Adding .SA for south american stocks
B3_tickers.index = B3_tickers.index.astype(str) + '.SA'

#Putting the tickers column back
B3_tickers.reset_index(level=0, inplace=True)
B3_tickers.rename(columns={'ticker':'tickers'}, inplace=True)

#Dropping duplicates
B3_tickers= B3_tickers.drop_duplicates(subset='tickers', keep="first")

#Saving stock names in csv file
B3_tickers.to_csv('B3_tickers.csv')



# Function that iterates through each ticker and gets data from the stock market, then saves each stock data
# in it's individual CSV file


def get_B3_from(source):
    
    #List for the stocks that had some error being collected
    error_stocks = []

    # Creates directory for the stock data CSV files
    if not os.path.exists('B3_stock_dfs'):
        os.makedirs('B3_stock_dfs')
    
    # When data collecting will start and end for the Dates
    global start
    global end
    
    print(f'>>>Getting Stock Data from {source} from {end}')

    #Iterating through each ticker
    for ticker in tqdm.tqdm( B3_tickers['tickers']):    
            
        
        # Reading data on the stock. If grabbing todays data failes, tries to grab data from yesterday 
        try:
            df=web.DataReader(ticker, source, start, end)   
        except:
            #Changing end date to yesterday
            end = (dt.datetime.now() - dt.timedelta(1)).strftime('%Y-%m-%d')
            df = web.DataReader(ticker, source, start, end)   

    
        #High/Low Open/Close percentage
        df['HL_pct'] = ((df['High'] - df['Low']) / df['Low'])*100 
        df['OC_pct'] = ((df['Close'] - df['Open']) / df['Open'])*100

        #Boolinger Band
        df['Middle Boolinger'] =   df['Adj Close'].rolling(20).mean()
        df['Sup_Boolinger'] =  df['Middle Boolinger'] + (2*df['Adj Close'].rolling(20).std())
        df['Inf_Boolinger'] =  df['Middle Boolinger'] - (2*df['Adj Close'].rolling(20).std())

        #Exponential Moving Mean
        df['Exp20_Close'] = df['Adj Close'].ewm(span=20, adjust=False).mean()

        #Expantion/Contraction of stock price
        df['Deviation_band'] = df['Adj Close'].rolling(20).std()
       
        #RSI
        change = df['Adj Close'].diff(1)

        gain = change.mask(change<0, 0)
        loss = change.mask(change>0, 0)
        avg_gain = gain.ewm(min_periods=rsi_period, com=rsi_period-1).mean()    
        avg_loss = loss.ewm(min_periods=rsi_period, com=rsi_period-1).mean()
        rs = abs(avg_gain / avg_loss)
        df['RSI'] = 100 - (100/(1+rs))

        '''
            Now the code will do a webscrape on some pages on yahoo finance to get more details and info. It will do this by table
            reading or span-string reading since some pages don't have tables. With table reading it's straight up but with span reading
            we need to get the reactID of each line we want. And for that it's kind of hardcoded, I read through all the span lines 
            and wrote down the useful ones.  
        '''

       


        #Reading into page
        resp = requests.get(f'https://finance.yahoo.com/quote/{ticker}/financials')
        #BeautifulSoup scrapes the page in TXT form
        soup = bs.BeautifulSoup(resp.text, 'lxml')

        #Number of span lines we got
        length = int(np.array(soup.find_all('span')).shape[0])

        #All lines with the span class, which has the info we want
        lines = np.array(soup.find_all('span'))

        #List to store the span lines that have the reactID codes we want
        spans = []

        #Dates we want to find
        find_dates = ['12/30/2019','12/30/2018','12/30/2017','12/30/2016']

        #List for the dates we actually find
        dates = []


        #Iterating through the lines and grabbing all lines from the span class
        for line in range(0,length):
            spans.append(BeautifulSoup(str(lines[line]), features='lxml').span)

        #Iterating through each date we want to find in the website
        for date in find_dates:

            #Iterating through each span-class line
            for line in range(0,length):

                #If the text line and date match then put the date in the found dates list
                if spans[line].string == date:
                    dates.append(spans[line].string)
                    break
            
        #Changes date format for indexing with the webreader dataframe
        for index, date in enumerate(dates): 
            
            #If any string dpesn't match the format than it's not a date and will be removed
            try:
                dates[index] = dt.datetime.strptime(date, "%m/%d/%Y").strftime("%Y-%m-%d") 
            except:
                
                #dates.remove will raise exception when there is no more of such content in the list, stopping the loop
                removed = False
                while(removed == False):
                    try:
                        dates.remove(dates[index]) 
                    except:
                        removed = True
                
                
        #Adding 3 days to the dates, because most stocks don't opperate on the last day of the year. Which is
        #the date time for the data to appear on the website.
        for index, date in enumerate(dates):
            dates[index] = (dt.datetime.strptime(date, '%Y-%m-%d') + dt.timedelta(3)).strftime('%Y-%m-%d')
                
                
        #Info we want to get from the webiste
        interesting_lines =['Total Revenue',
                     'Cost of Revenue',
                     'Gross Profit',
                     'Selling General and Administrative',
                     'Total Operating Expenses',
                     'Operating Income or Loss',
                     'Interest Expense',
                     'Total Other Income/Expenses Net',
                     'Income Before Tax',
                     'Income Tax Expense',
                     'Income from Continuing Operations',
                     'Net Income',
                     'Net Income available to common shareholders',
                     'EBITDA']
        
        #List for the info we actually find on the website
        infos = []

        #List for the ReactIDs of the lines that have the data about the infos above
        number_ids = []

        #Column renaming
        column_names=['Total Revenue (TTM)',
           'Cost of Revenue (TTM)',
           'Gross Profit (TTM)',
           'Selling General and Administrative Expenses (TTM)',
           'Total Operating Expenses (TTM)',
           'Operating Income or Loss (TTM)',
           'Interest Expense (TTM)',
           'Total Other Income/Expenses Net',
           'Income Before Tax (TTM)',
           'Income Tax Expense (TTM)',
           'Income from Coninuing Operations (TTM)',
           'Net Income (TTM)',
           'Net Income available to Shareholders (TTM)',
           'EBITDA (TTM)']        


        #Iterating through the informations we want
        for index, info in enumerate(interesting_lines):
            
            #Boolean for if the information was found
            check = False

            #Iterating through the span lines
            for line in range(0,length):

                #If line contains the information we want, appends it to the found infos list.
                if spans[line].string == info:
                    infos.append(spans[line].string)

                    #Appends the info's reactID +5, one line below, where the numbers and data are
                    number_ids.append( str( int(spans[line]['data-reactid'])+5 ) )
                    check = True
                    pass
            
            #In case the information isn't found, the respective column name is changed to a NAN, to be removed later
            if check == False:
                column_names[index] = np.nan
            
    
        #Removing NANs from column name list
        column_names = [c for c in column_names if str(c) != 'nan']   


        #Creating the columns for the information
        for column in column_names:
            df[f'{column}'] = np.nan
    
        #Iterating through dates, with indexing
        for index, date in enumerate(dates):     

            #Iterating through new columns, with indexing
            for column, string in enumerate(column_names):

                #Iterating through span lines
                for line in range(0,length):

                    #Fetching data for the respective information column in order
                    if spans[line]['data-reactid'] == number_ids[column]:

                        #Locates the date in dataframe index, formats the string of the data, turns it into a Integer and
                        #puts the data in it's correct place in time.
                        try:
                            df[f'{string}'].loc[dates[index]] = int((spans[line].string).replace(',',''))
                        except Exception as e:
                            print(e)
                            print (f'Error formating/alocating string to int for stock {ticker}')
                            
                            #Appending to stocks with errors list
                            error_stocks.append(ticker)
                            continue      
            #Adding 2 to the IDs for each iteration so we get the lines of previous dates for the information
            number_ids = [int(c) for c in number_ids]
            number_ids = [c+2 for c in number_ids]
            number_ids = [str(c) for c in number_ids]       
            
        
        
        #Page URL that we will pass to PhantomJS
        url = f'https://finance.yahoo.com/quote/{ticker}/key-statistics'

        #Initiating PhantomJS
        driver = PhantomJS(executable_path=r'phantomjs.exe')

        #Opening URL with PhantomJS to fully load the page
        driver.get(url)

    

        #Returning page source after all the JavaScript codes have been loaded
        resp = driver.page_source

        #Closing PhantomJS
        driver.quit()

        #List of tables that Pandas found in the web page
        dfs = pd.read_html(resp)

        #Dataframe to put all the tables in just one
        key_stats = pd.DataFrame()

        #Iterating through the tables
        for dframe in dfs:
    
            #If dataframe is empty, passes the first table
            if key_stats.empty:
                key_stats=dframe
    
            #If it already has a table, appends the new ones
            else:
                key_stats = key_stats.append(dframe)
        
        #Fixing dataframe index, with numbers from 0 to length of dataframe 
        key_stats.index = [c for c in range(0,key_stats.shape[0])]

        #There´s some info that we don´t have interest so we drop what we don´t need
        stats = key_stats.loc[:8]

        #Removing columns 0 and 1
        stats = stats.drop([0,1],axis=1)

        #Passing the information names as the dataframe index
        stats.index = [c for c in stats['Unnamed: 0'].values]

        #Removing the column with information names, since it´s all in the index 
        stats = stats.drop(['Unnamed: 0'],axis=1)

        #Transposing the dataframe, so that the Dates become the index and the information names become the column
        stats = stats.transpose()

        #Criating the new columns in the main dataframe
        for column in stats.columns:
            df[f'{column}'] = np.nan

    
        #Putting all the dates in a list 
        dates = [c for c in stats.index]

        #Iterating through the dates
        for index, date in enumerate(dates): 
            #Changing date format
            try:
                dates[index] = dt.datetime.strptime(date, "%m/%d/%Y").strftime("%Y-%m-%d")
            except:
                #One of the dates actually has more things than the date so we remove all that
                date = date.replace('As of Date: ','')
                date = date.replace('Current','')
                dates[index] = dt.datetime.strptime(date, "%m/%d/%Y").strftime("%Y-%m-%d")
    
        #Adding 3 days because stocks don´t opperate in the last day of the year
        for index, date in enumerate(dates):
            dates[index] = (dt.datetime.strptime(date, '%Y-%m-%d') + dt.timedelta(3)).strftime('%Y-%m-%d')

        #Passing changed dates back into the dataframe´s index
        stats.index = dates

        #Iterating through dates again
        for date in stats.index:
            
            #Iterating through the new columns
            for column in stats.columns:

                #Locating the dates and columns in the main dataframe and putting the respetive data in it´s place
                try:
                    df[f'{column}'].loc[date] = stats[f'{column}'].loc[date]
            
                #If any errr occurs in this process, shows the error for the respective stock and adds it to the
                #stocks-with-error list
                except Exception as e:
                    print(e)
                    print (f'Error formating/alocating string to int for stock {ticker}')
                            
                    #Appending to stocks with errors list
                    error_stocks.append(ticker)



        '''
        Since we only have info year by year and the .loc funtion only puts the data in the specific index, we need to
        fill the NANs with the previous data that isn't a NAN (ffill method). This way, from each data alocated, all future 
        lines will have this exact data, until a new data (the most recent) appears, and the process repeats.
        ''' 
        df.fillna(method='ffill', inplace=True)


       
        # Saving csv file
        df.to_csv('B3_stock_dfs/{}.csv'.format(ticker))

    #Showing any stocks with errors if there are any
    if error_stocks != []:
        print('\n ------ Inspect Errors ------- \n')
        print([c for c in error_stocks] )


# Calling function
get_B3_from('yahoo')





