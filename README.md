# Stock Solver
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Project Status](https://img.shields.io/badge/status-in%20development-orange)](#current-progress)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](pyproject.toml)

<!-- TODO: Rephrase this to be "within the scope of minimal demo" -->
Toy project to predict and analyze stock market. Currently under active development. Current implementation covers data collection, dataset construction, and an Informer-based model built with PyTorch. All components are implemented from scratch for learning purposes.

# Overview and Goals

- **Data** - We collect data from [Alpha Vantage](https://www.alphavantage.co/) via a simple API wrapper we implemented. We collect daily time series (OCHLV values), new sentiment scores, and insider trading data for selected tickers. We combine everything into a neat PyTorch Dataset.
- **Model** - We wanted to implement a Deep Learning model for predicting Closing Prices few days into the future. Since, this is a Seq2Seq problem, we landed on using Transformer architecture, more specifically an Informer architecture introduced in this [paper](https://arxiv.org/abs/2012.07436). This could be not the state-of-the-art approach, but for the sake of this scope, we think this is a great choice.

## Current Progress
- [x] **Data access**:
    - [x] [Time Series endpoint](https://www.alphavantage.co/documentation/#daily)
    - [x] [News Sentiment endpoint](https://www.alphavantage.co/documentation/#news-sentiment)
    - [x] [Insider Transactions endpoint](https://www.alphavantage.co/documentation/#insider-transactions) (Available, but not used anywhere)
    - [x] [Company Overview endpoint](https://www.alphavantage.co/documentation/#company-overview)
- [x] **Populating the Dataset**:
    - [x] Basic preprocessing and aggregation of the features
    - [x] Per-ticker normalization
    - [x] "Unrolled" torch dataset
- [x] **Model Implementation**:
    - [x] Encoder
    - [x] Decoder
    - [x] Distillation
    - [x] ProbSparse Attention
    - [x] Embedding
- [ ] **Model Evaluation**:

## Data Pipeline
Our approach for the data pipeline is quite straightforward and can be depicted below. 
```mermaid
flowchart TD
    subgraph INGEST[Alpha Vantage Wrapper]
        AV[AV Module]:::code
        TS[Daily Time Series]:::data
        NS[News Sentiment]:::data
        AV --> FI[Filter Tickers]
        FI --> TS
        FI --> NS
        TS --> Concat([+])
        NS --> Concat
    end
    A["Fetch Tradable Symbols (Alpaca)"]--> AV
    FM["Per Ticker Feature Matrix (Time*Features)"]:::artifact
    Concat --> FM
    FM --> DA[Torch Dataset]
```
First, we obtain the list of available tickers using [Alpaca API](https://alpaca.markets/) to gain an initial list of active tickers in the US market. However, using this approach alone, leaves us with almost 13,000 tickers. We further filter out the list of tickers using Company Overview endpoint provided by [Alpha Vantage](https://www.alphavantage.co/). We filter with the criteria that the ticker is a common stock, so no cryptocurrencies, and has a minimum market capitalisation of 1,000,000,000$. This leaves us with around 2,000 tickers. For each ticker we collect the data by calling Daily Time Series and News Sentiment end points. The time series end point returns all of the available information in one call. However, with news sentiment, we have to call in small time intervals to cover the whole range.

## Getting Started
1. Clone the repository
    ``` bash
    git clone https://github.com/KYZZHECIK/stock_solver.git && cd stock_solver
    ```
2. Install dependencies. We use [Poetry](https://python-poetry.org/docs/) as our dependencies manager.
    ``` bash
    poetry install
    ```
3. Set environment variables for accessing the APIs.
    
    Create a `.env` file containing your Alpha Vantage API key.
    ``` bash
    ALPHA_VANTAGE_API_KEY="your_key"
    ```
    Additionally, if Alpaca API is also needed, append the necessary keys to `.env`.
    ``` bash
    ALPACA_SECRET_KEY="your_secret_key"
    ALPACA_API_KEY="your_key"
    ```

4. Run.

    For obtaining filtered list of tickers, run:
    ``` bash
    python -m src.stock_solver.dataset.apis.get_tickers --path=...
    ```
    The command above will call Alpaca API to obtain the available tickers, filter using Alpha Vantage Overview endpoint, and save the tickers to the specified path. If there is a preditermined list of tickers available, this step can be skipped. 

    For obtaining the data necessary for the dataset, run:
    ``` bash
    python -m src.stock_solver.dataset.apis.alpha_vantage_calls --tickers_path=... --dataset_path=...
    ```
    The command will start calling the end points and aggregating the features for each ticker from the `--tickers_path` file. The features for each ticker will be saved in the `--dataset_path` folder.