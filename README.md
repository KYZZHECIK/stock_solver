# Stock Solver
Toy project to predict and analyze stock market

---

# Roadmap

I want to build a dataset for daily closing price prediction. For that, first I will implement an API wrapper for Alpha Vantage endpoints.
Using the responses from the API, we can start building the dataset. Using the Time Series endpoints
(for example intra day, dayly, weekly, and monthly) we can build the most basic feature set. From that, we can also obtain our target
values (closing price, for example, at the end of the day). Additionally, we can use additional information that API provides.
For example, some that caught my eye are the news sentiment and insider trades. Maybe, later on we could include some additional features.


## Current Progress

### Alpha Vantage API Wrapper
- [x] Time Series (Intraday, day, week, month)
- [x] News sentiment 
- [x] Insider Trades

### Torch Dataset
    
### Model
