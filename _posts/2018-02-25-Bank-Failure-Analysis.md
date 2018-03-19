---
layout: default
title: Bank Failure Analysis
---

## Visualizing Bank Failures in the USA with Python & geoplotlib, Years: 2000-2017

This analysis was done to visualize bank closures over the last 17 years. The FDIC is often appointed as receiver for failed banks, and provide a [list](https://catalog.data.gov/dataset/fdic-failed-bank-list) of banks which have failed since October 1, 2000. 

## Methods

Using python and the FDIC data, bank closures were mapped using [geoplotlib](https://github.com/andrea-cuttone/geoplotlib) and graphed with pandas. Geoplotlib requires data to contain latitude and longitude data, in the following nomenclature: name, lat, lon. Latitude and longitude information was joined from [here](http://notebook.gaslampmedia.com/wp-content/uploads/2013/08/zip_codes_states.csv). A key column was made in both data sets and a merge was done in order to get proper coordinates. 

## Results

### Viewing Bank Closure Data with geoplotlib
<img src="/img/bank/Bank_Map.png" height="100%" width="100%" class="inline"/>

### Closures Peaked in 2009-2010
<img src="/img/bank/Bank_Year.png" height="100%" width="100%" class="inline"/>

### Georgia Led in Bank Failures
<img src="/img/bank/Bank_State.png" height="100%" width="100%" class="inline"/>

Ulitmately closures peaked during the height of the financial crisis. Georgia's banking closures, which stand out in number from the rest, have been [written](http://www.nytimes.com/2010/04/12/opinion/12krugman.html) about. It seems that GA just had a lot of small banks where loans went bad. 

