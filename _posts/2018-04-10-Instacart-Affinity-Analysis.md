---
layout: default
title: Instacart Affinity Analysis 
---

## Instacart - Visualizing Products Purchased Together

Last year, Instacart joined the open data movement and released information on over 3 million orders in hopes of spurring new ways of analyzing their data. The [anonymized dataset](https://tech.instacart.com/3-million-instacart-orders-open-sourced-d40d29ead6f2) contains a sample of orders from over 200k Instacart users. 

This data is great for testing machine learning and data mining models to better understand shopping patterns. Instacart even sponsored a [kaggle contest](https://www.kaggle.com/c/instacart-market-basket-analysis) just for that purpose. Let's see what we could learn from a simple affinity analysis!

## Methods

Using Python, Instacart data was merged into one complete file and processed to learn which departments are more often shopped together when an order is placed. 

## Results

### Top Departments
<img src="/img/instacart/Departments.JPG" height="100%" width="100%" class="inline"/>

Looks like instacart users eat realitely healthy, with produce and dairy eggs showing highest amount of purchases. This is quickly followed by beverages, frozen food, and snacks. 

### Visualizing Department Affinity
<img src="/img/instacart/Dept_matrix.JPG" height="100%" width="100%" class="inline"/>

Produce and dairy eggs departments are most often found bundled together, while snacks are usually brough with almost every department! 

### Top 25 Departments Shopped Together
<img src="/img/instacart/Top25dept.JPG" height="100%" width="100%" class="inline"/>

Another way of looking at the matrix shows us the same pattern. While dairy eggs and produce are most often bough together, they are often bundled with snacks and beverages. 
