---
layout: post
title: MTA Analysis!
---

# Analyzing Changing MTA Subway Ridership Patterns in Downtown Brooklyn

Downtown Brooklyn has seen an explosion in recent developments. As real estate prices rise in tandem with adjacent luxury towers, so do hopes and regrets. 

In his piece, [Don't You Be My Neighbor](http://nymag.com/nymetro/realestate/urbandev/features/n_10289/), Colson Whitehead sums it up with his first sentence:

> "I used to live in Fort Greene, and whenever I visit my old neighborhood, I am tormented by the same absurd thought: I should have bought that crack house when I had the chance."

The 2004 [rezoning](https://www.brooklyn-usa.org/wp-content/uploads/2016/02/Downtown-Brooklyn-2004-Rezoning_Final.pdf) of Dowtown Brooklyn added almost 10M sf of residential space and over 1M sf of both office and retail space. 

It was interesting then to look at the most obvious place of impact: The MTA Subway system, which still remains the primary source of transportation for millions of New Yorkers. 

Using Python and [MTA Turnstile Data](http://web.mta.info/developers/turnstile.html), Downtown Brooklyn subway stations were analyzed to show changes in monthly ridership. 

## Python Code

### Scraping MTA Data and Saving as .csv Files

```python
from datetime import datetime, timedelta
import pandas as pd
import time

def get_data():

    end_date = datetime.strptime(time.strftime("%y%m%d"), '%y%m%d')
    begin_date = datetime.strptime('170916', '%y%m%d')
    base_link = 'http://web.mta.info/developers/data/nyct/turnstile/turnstile_'

    while(begin_date < end_date):

        link = '{0}{1}.txt'.format(base_link, begin_date.strftime("%y%m%d"))
        print ("Retrieving data from...")
        df = pd.read_csv(link)
        df.to_csv('{0}.csv'.format(begin_date.strftime("%y%m%d")), index=False)
        
        begin_date = begin_date + timedelta(days=7)      
```

### Reading the .csv Files to Isolate Station Data

```python
import glob
import pandas as pd

allFiles = glob.glob("*.csv")
frame = pd.DataFrame()
list_ = []
for file_ in allFiles:
    df = pd.read_csv(file_,index_col=None, header=0)
    list_.append(df)
frame = pd.concat(list_)

station = frame.loc[frame['STATION'] == 'DEKALB AV']

station.to_csv('dekalb.csv', sep=',')

```


### Analyzing Station Data

```python
%matplotlib inline

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

#load data and parse data column as datetime
df = pd.read_csv('dekalb.csv', parse_dates=[7])

#adding a month and year column for analysis
df['year'], df['month'] = df['DATE'].dt.year, df['DATE'].dt.month

#filtering only specific rows based on the below criteria for cleaner data
df1 = df[(df.LINENAME == 'BDNQR') & (df.DESC == 'REGULAR') & (df.year >= 2016) & (df.year <= 2017)]

#Grouping cummalitve entries by date
df1 = df1.groupby( [ "DATE", "TIME", 'year', 'month'], as_index=False )[["ENTRIES"]].sum()

#Calculating difference in daily cummulative entries to find actual number of entry per day (delta)
df1['delta'] = df1['ENTRIES'] - df1['ENTRIES'].shift(1)

#Grouping delta  by day
df2 = df1.groupby( ["DATE", 'year', 'month'], as_index=False )[["delta"]].sum()

#Getting rid of outliers
df3 = df2[(df2.delta >= 0) & (df2.delta <= 40000)]

#Plot and analyze

df3pivot = pd.pivot_table(df3,index=["month"],values=["delta"],
               columns=["year"],aggfunc=[np.sum])
print(df3pivot)

df3pivot.plot(kind = 'bar')

```

## Results

As expected ridership increased in Downtown Brooklyn. 

Dekalb saw almost 1M more people enter the station YoY 2016 vs 2017, rising 17%. Ridership increased consistently every month in 2017 vs 2016. 

<img src="/img/dekalb.png" height="50%" width="50%" class="inline"/>
