# Analyzing Changing MTA Subway Ridership Patterns in Downtown Brooklyn

Downtown Brooklyn has seen an explosion in recent developments. As real estate prices rise in tandem with adjacent luxury towers, so do hopes and regrets. 

In his piece, [Don't you be my Neighbor](http://nymag.com/nymetro/realestate/urbandev/features/n_10289/), Colson Whitehead sums it up with his first sentence:

> I used to live in Fort Greene, and whenever I visit my old neighborhood, I am tormented by the same absurd thought: I should have bought that crack house when I had the chance.

The 2004 [rezoning](https://www.brooklyn-usa.org/wp-content/uploads/2016/02/Downtown-Brooklyn-2004-Rezoning_Final.pdf) of Dowtown Brooklyn added almost 10M sf of residential space and over 1M sf of both office and retail space. 

It was interesting then to look at the most obvious place of impact: The MTA Subway system, which still remains the primary source of transportation for millions of New Yorkers. 

Using Python and [MTA Turnstile Data](http://web.mta.info/developers/turnstile.html), Downtown Brooklyn subway stations were analyzed to show changes in monthly ridership. 

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


