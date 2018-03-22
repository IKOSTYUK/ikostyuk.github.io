---
layout: default
title: MTA Analysis
---

## Analyzing Changing MTA Subway Ridership Patterns in Downtown Brooklyn

 Downtown Brooklyn is seeing an explosion in recent developments. As real estate prices rise in tandem with adjacent luxury towers, so do hopes and regrets. 

In his piece, [Don't You Be My Neighbor](http://nymag.com/nymetro/realestate/urbandev/features/n_10289/), Colson Whitehead sums it up with his first sentence:

> "I used to live in Fort Greene, and whenever I visit my old neighborhood, I am tormented by the same absurd thought: I should have bought that crack house when I had the chance."

The 2004 [rezoning](https://www.brooklyn-usa.org/wp-content/uploads/2016/02/Downtown-Brooklyn-2004-Rezoning_Final.pdf) of Dowtown Brooklyn added almost 10M sf of residential space and over 1M sf of both office and retail space. 

It was interesting then to look at the most obvious place of impact: The MTA Subway system, which still remains the primary source of transportation for millions of New Yorkers. 


## Methods
 

 Using Python and [MTA Turnstile Data](http://web.mta.info/developers/turnstile.html), Downtown Brooklyn subway stations were analyzed to show changes in monthly ridership. All of the individual .csv files were downloaded and saved locally using [download.py](https://github.com/IKOSTYUK/MTA-Project/blob/master/download.py). Then one complete dataframe was created by combining all of the saved csv files using [read.py](https://github.com/IKOSTYUK/MTA-Project/blob/master/read.py). Finally, the data was sliced and diced by filtering for specific stations and different station devices: [analyze.py](https://github.com/IKOSTYUK/MTA-Project/blob/master/analyze.py).



## Results

As expected ridership increased in Downtown Brooklyn. 

### Dekalb saw almost 1M more people enter the station YoY 2017 vs 2016, rising 17%. 

<img src="/img/mta/deklab.png" height="100%" width="100%" class="inline"/>

### Jay St saw a 9% and 3% uptick in their R and ACF entrances respectively. 

<img src="/img/mta/jay-r.png" height="100%" width="100%" class="inline"/>
<img src="/img/mta/jay-acf.png" height="100%" width="100%" class="inline"/>

### Borough Hall saw a 10% (+75K) and 5% (+360K) uptick in their R and 2345 entrances respectively

<img src="/img/mta/BHR.png" height="100%" width="100%" class="inline"/>
<img src="/img/mta/BH2345.png" height="100%" width="100%" class="inline"/>



 
