# Forecasting prices IMA bootcamp

This repository explores multiple forecasting methods to predict the cost of trucking for a logistics company for the next 3-12 months.

See White Paper.pdf for a deatiled descrpition of the project, including the methods and results.

## Description

The main goal is to predict the cost of trucking for 3-12 months away based on historical data. For a specified trucking route, there is data given in the form of a time series, giving the weekly cost of trucking between 2017 and 2021. (The data presented here is a sanitized version of real data, as to protect the company.) 

### Univariate models

First, we established a baseline by running some univaritate model tests, including seasonal niave (SNaive), season-trend loss (STL),  seasonal auto-regressive integrated moving average (SARIMA), and TBATS. To assess model accuracy, we implemented a cross validation routine with a rolling
origin and 12-week forecasts to backtest forecasts against actual cost values. 

### Multivariate models

We selected external regressors (maximum temperture, precipitation, and diesel fuel prices) to incorporate with SARIMA. This data was obtained from public sources, namely https://data.gov/.

### Market scenario clustering

The folder "Market scenario clustering" is dedicated to a case study on a specific trucking lane using market scenarios. In particular, we looked at the Pheonix trucking costs, becasue lettuce forms a significant portion of the shipping volume. Forecasts of trucking costs out of the Phoenix freight market should reflect knowledge about the state of the lettuce market.

First, we captured the state of the lettuce market via weekly time series data of lettuce prices. We performed K-Means Clustering with three clusters to categorize each week of the lettuce market into one of three possible scenarios (normal market, market shock, and transition).  Afterwards, the scenario classification becomes an input into the forecasting model.

## Authors

Elizabeth Sprangel
(elizabethsprangel@gmail.com)

## Acknowledgments

This work was completed as a part of the IMA Math-to-Industry Bootcamp in partnership with the company C.H. Robinson.
