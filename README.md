# Stock Solver
Toy project to predict and analyze stock market

---

# TODOA/Roadmap

I want to build a dataset for daily closing price prediction. I will start with some basic features for time series like OHLC values (adjusted close if available), we will also include News sentiment scores for the monthly if they are available, potentially, if they are available we could use the insider trading endpoint for some interesting insight.

After that when data collection is done, we will be desiging the Transformer-like architecture, probably multimodel, one submodel to deal with financial information and the other one to deal with outsider features (news, insider trading). I would aim for a multivariate model, but for the proof of concept we will stick to a single stock prediction. We will be predicting daily close values.

[ ] Data collection
    [ ] Time Series Daily
    [ ] Time Series IntaDaily
    [ ] Time Series Montly
    [ ] News sentiment 
    [ ] Insider Trades

[ ] Model