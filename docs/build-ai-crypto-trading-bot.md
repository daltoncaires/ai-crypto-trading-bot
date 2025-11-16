# How to Build an AI Crypto Trading Bot

**by [Cryptomaton](https://www.coingecko.com/author/Cryptomaton) | Edited by [Brian Lee](https://www.coingecko.com/author/Brian%20Lee) - Updated September 26 2025**

The rapid advancement of Artificial Intelligence (AI) has introduced powerful new tools for traders. Unlike traditional rule-based bots that follow static instructions, AI-powered systems can analyze complex market data, adapt to changing conditions, and identify subtle patterns that humans might miss. This has led many traders to explore building AI crypto trading bots to gain a competitive edge.

In this step-by-step tutorial, we'll build a functional AI crypto trading bot in Python. We will use the [CoinGecko API](https://www.coingecko.com/en/api) for comprehensive market and on-chain data and an OpenAI large language model (LLM) as the decision-making core.

![How to Build an AI Crypto Trading Bot Step-by-step Guide](https://assets.coingecko.com/coingecko/public/ckeditor_assets/pictures/34052/content_Build_AI_Crypto_Trading_Bot.webp)

* * *

## What Is an AI Crypto Trading Bot?

An AI crypto trading bot is software that automates cryptocurrency trades by utilizing artificial intelligence to analyze market data and make informed decisions.

Unlike traditional algorithmic trading bots, which rely on fixed "if-then" rules, AI bots can learn from data, adapt to new conditions, and detect nuanced patterns that rigid systems might miss.

Key advantages include:

*   **Dynamic logic**: AI bots can dynamically adjust strategies by modifying the prompt, thereby enhancing testing speed and reducing iteration time.
*   **24/7 operation**: They run continuously without fatigue, monitoring markets around the clock.
*   **No emotions**: Trades are based on analysis rather than fear or greed, reducing impulsive errors.
*   **Handling complex variables**: Beyond basic indicators like RSI or MACD, they can incorporate diverse factors such as on-chain metrics, sentiment, or emerging trends for more informed strategies.

## How Does an AI Trading Bot Work?

AI trading bots work by ingesting market data and using an AI engine to evaluate it for trade opportunities, in accordance with a well-crafted user prompt.

At a high level, an AI trading bot's workflow breaks down into four main stages:

![](https://assets.coingecko.com/coingecko/public/ckeditor_assets/pictures/34049/content_flowchart.webp)

*   **Data Layer**: This stage involves ingesting real-time and historical crypto data from sources like the CoinGecko API. This may include any time series data.
*   **User Settings**: This includes the prompt and any specific trading instructions, such as Stop Loss and Take Profit.
*   **AI Engine**: Data & prompts are ingested by the AI engine, which is typically powered by an LLM like OpenAI, to produce a recommendation.
*   **Safety Checks**: Hard-coded rules like Stop Loss and Take Profit are applied, along with additional safeguards such as CoinGecko's honeypot checks to verify liquidity pool integrity and avoid scams.
*   **Trade Layer**: The bot places trades based on the validated signal. For beginners, it is highly encouraged to start with paper trading to test strategies in a risk-free environment before deploying live funds on a CEX or DEX.
*   **Data Access Layer (DAL)**: Trades are stored locally for reporting purposes. The trade engine regularly checks if any order may be closed in accordance with the Take Profit or Stop Loss rules.

## Prerequisites

Here’s what you’re going to need to complete this project:

*   A CoinGecko API Key
*   Python 3.11+
*   An OpenAI API Key

### Obtaining a CoinGecko API Key

All endpoints used in this guide can be accessed with a free Demo API key. If you don’t have one, follow this guide to [get your free Demo API key](https://support.coingecko.com/hc/en-us/articles/21880397454233-User-Guide-How-to-sign-up-for-CoinGecko-Demo-API-and-generate-an-API-key).

AI trading bots may make frequent data requests, and can cause the Demo plan's rate limits to be exhausted quickly. For production use or intensive backtesting, upgrading to a paid plan is recommended.

[![Subscribe to CoinGecko API](https://assets.coingecko.com/coingecko/public/ckeditor_assets/pictures/34010/content_Subcribe_to_CoinGecko_API_CTA_-_DEX.webp)](https://www.coingecko.com/en/api/pricing)

For this project, we’ll be using the following CoinGecko API endpoints:

*   [Coin Price by IDs](https://docs.coingecko.com/reference/simple-price)
*   [Coin OHLC Chart by ID](https://docs.coingecko.com/reference/coins-id-ohlc)
*   [Coins List with Market Data](https://docs.coingecko.com/reference/coins-markets)
*   [Search Pools](https://docs.coingecko.com/reference/search-pools)

### Obtaining an OpenAI API Key

To obtain an OpenAI API key, log in to your OpenAI account and navigate to API Keys under Organization.

Click **+Create New Secret Key** in the top right corner and copy the key.

### Setting Up The Project Environment

To get started, create a new directory for your project:
```bash
mkdir ai-crypto-bot
cd ai-crypto-bot
```

Next, set up a Python virtual environment to isolate your project's dependencies:
```bash
python -m venv env
# Activate on Windows
env\Scripts\activate
# On Linux/Mac
source env/bin/activate
```

### Installing Dependencies

Install the required packages by creating a `requirements.txt` file in the project root with the following content:
```
annotated-types==0.7.0
anyio==4.10.0
certifi==2025.8.3
charset-normalizer==3.4.3
colorama==0.4.6
dataclass-wizard==0.35.1
distro==1.9.0
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
idna==3.10
jiter==0.11.0
openai==1.108.1
pydantic==2.11.9
pydantic_core==2.33.2
python-dotenv==1.1.1
requests==2.32.5
sniffio==1.3.1
tqdm==4.67.1
typing-inspection==0.4.1
typing_extensions==4.15.0
tzdata==2025.2
urllib3==2.5.0
```

Now install them by running:
```bash
pip install -r requirements.txt
```

### Storing Credentials and Settings

Create a `.env` file in the project root to store API keys and trading configuration.

Copy this template:
```
CG_API_KEY = "CG-API-KEY"
OPENAI_API_KEY="sk-OPENAI-API-KEY"

# Application Settings
TAKE_PROFIT = "20"
STOP_LOSS = "10"
ORDER_AMOUNT = "50"
PRICE_CHANGE = "3"

# Pool Safety Checks
MIN_VOLUME_24H = "1000000"
MIN_RESERVES_USD="1000000"
MIN_BUYS_24H = "1000"

# Prompt Settings
PROMPT_TEMPLATE = ./prompt_template.txt
```

Replace the placeholder API keys with your actual CoinGecko API key and OpenAI API key.

Here's what each setting does:

*   **TAKE_PROFIT:** The percentage gain threshold to sell and lock in profits (e.g., 20% above entry price).
*   **STOP_LOSS:** The percentage loss threshold to sell and cut losses (e.g., 10% below entry price).
*   **ORDER_AMOUNT**: The fixed USD amount to allocate per trade.
*   **MIN_VOLUME_24H**: Minimum trading volume (in USD) for a pool to qualify as safe.
*   **MIN_RESERVES_USD**: Minimum liquidity reserves (in USD) to filter out low-liquidity pools.
*   **MIN_BUYS_24H**: Minimum number of buys in the last 24 hours to indicate genuine activity.
*   **PROMPT_TEMPLATE**: Path to the file containing the AI prompt template.

Create a `prompt_template.txt` file in your project root. We will store our system prompt in this separate file, which will be referenced in our .env file. We will define the prompt's content later in the guide.

To load your config, create a new file under `utils/load_env.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

cg_api_key = os.getenv("CG_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
prompt_template = open(os.getenv("PROMPT_TEMPLATE"), "r").read()

# Trade Settingd
tp = float(os.getenv("TAKE_PROFIT"))
sl = float(os.getenv("STOP_LOSS"))
qty = float(os.getenv("ORDER_AMOUNT"))
price_change = float(os.getenv("PRICE_CHANGE"))

# Pool Safety Checks
min_volume_24h = float(os.getenv("MIN_VOLUME_24H"))
min_reserves_usd = float(os.getenv("MIN_RESERVES_USD"))
min_buys_24h = float(os.getenv("MIN_BUYS_24H"))
```

## How to Feed Real-time & Historical Crypto Market Data to AI?

You can feed real-time and historical crypto market data to an AI trading from a comprehensive data source like the CoinGecko API. This data is crucial for the AI to perform its analysis. The CoinGecko API provides a wide range of data points, including real-time prices, historical OHLC (Open, High, Low, Close) candlestick data, market cap, and liquidity data, which are essential for building a robust trading strategy.

### Fetching Data: How to Get Historical Data for Major Coins?

Under `services/coingecko_service.py`, we’re going to define a `CoinGecko` class, with a method for each endpoint.

Start by importing the required dependencies and define the constructor to include the CoinGecko authentication headers. Don’t worry about any types that you have not yet defined.
```python
import requests
from data_access.models.coin import Coin
from utils.load_env import *
from typing import List
from datetime import datetime

class CoinGecko:
    def __init__(self):
        self.root = "https://pro-api.coingecko.com/api/v3"
        self.headers = {
            "accept": "application/json",
            "x-cg-pro-api-key": f"{cg_api_key}",
        }
```

**Note:** If you’re using the Demo API, you’ll need to change the `self.root` URL to `https://api.coingecko.com/api/v3` and update the `self.headers` key to `x-cg-demo-api-key`.

Next, add a new method to the class to fetch OHLC data by coin ID:
```python
def get_historic_ohlc_by_coin_id(
    self,
    coin_id: str,
    vs_currency: str = "usd",
    days: int = 1,
    interval: str = "hourly",
):
    request_url = f"{self.root}/coins/{coin_id}/ohlc?vs_currency={vs_currency}&days={days}&interval={interval}"
    response = requests.get(request_url, headers=self.headers)
    candles = response.json()
    return candles
```

💡 **Pro tip**: The coin ID is a unique identifier for each cryptocurrency and may not always match the coin's ticker symbol. You can find the complete list of coin IDs via the [/coins/list](https://docs.coingecko.com/reference/coins-list) endpoint or by referencing [this spreadsheet](https://docs.google.com/spreadsheets/d/1wTTuxXt8n9q7C4NDXqQpI3wpKu1_5bGVmP9Xz0XGSyU/edit?usp=sharing).

To run this, instantiate the class and call the method with the desired parameters:
```python
cg = CoinGecko()
print(cg.get_historic_ohlc_by_coin_id("bitcoin", "usd", days=180, interval="daily"))
```

This will return raw candlestick data, along with a timestamp for search entry:
```json
[
    {
        "coinId": "bitcoin",
        "symbol": "btc",
        "realizedPnl": 0.0,
        "priceChange": -0.10940523691445969,
        "prices": [
            [1758380400000, 115977.0, 116048.0, 115925.0, 116039.0],
            [1758384000000, 116073.0, 116154.0, 116000.0, 116011.0],
            [1758387600000, 116033.0, 116083.0, 115925.0, 116069.0]
        ],
        [...]
    },
    {...}
]
```

Continue by creating methods for the remaining CoinGecko endpoints, and nest them under the `CoinGecko` class.

The following methods will enable our AI crypto trading bot to fetch real-time prices, identify promising large caps, and find safe liquidity pools:
```python
def get_price_by_coin_id(self, coin_id: str):
    request_url = self.root + f"/simple/price?ids={coin_id}&vs_currencies=usd"
    response = requests.get(request_url, self.headers)
    data = response.json()
    return data.get(coin_id, {}).get("usd")

def get_coins(self) -> List[Coin]:
    request_url = (
        self.root
        + "/coins/markets?order=market_cap_desc&per_page=250&vs_currency=usd&price_change_percentage=1h"
    )
    response = requests.get(request_url, headers=self.headers)
    data = response.json()
    coins = []
    now = datetime.now().timestamp()
    for coin_data in data:
        coin = Coin(
            coin_id=coin_data["id"],
            symbol=coin_data["symbol"],
            realized_pnl=0.0,
            price_change=coin_data.get(
                "price_change_percentage_1h_in_currency", 0.0
            ),
        )
        coin.prices = [[now, coin_data["current_price"]]]
        coins.append(coin)
    return coins

def search_pools(self, query: str = None, chain: str = None):
    request_url = f"{self.root}/onchain/search/pools?query={query}"
    response = requests.get(request_url, headers=self.headers)
```

### Defining Data

Under `data_access/models/`, we’re going to define the three main object types that we’ll be working with: `Coin`, `PaperOrder`, and `PortfolioItem`

**`data_access/models/coin.py`:**
```python
from dataclasses import dataclass, field
from typing import List
from dataclass_wizard import JSONWizard

@dataclass
class Coin(JSONWizard):
    coin_id: str
    symbol: str
    realized_pnl: float = 0.0
    price_change: float = 0.0
    prices: List[list] = field(default_factory=list)
```

**`data_access/models/paper_order.py`**
```python
from typing import Literal
from dataclasses import dataclass
from datetime import datetime
from dataclass_wizard import JSONWizard

@dataclass
class PaperOrder(JSONWizard):
    timestamp: datetime
    buy_price: float
    quantity: float
    symbol: str
    direction: Literal["BUY", "SELL"]
```

**`data_access/models/portfolio_item.py`**
```python
from dataclasses import dataclass, field
from typing import List
from datetime import datetime
from dataclass_wizard import JSONWizard

@dataclass
class PnLEntry(JSONWizard):
    date: datetime
    value: float

@dataclass
class PortfolioItem(JSONWizard):
    cost_basis: float
    total_quantity: float
    symbol: str
    pnl_entries: List[PnLEntry] = field(default_factory=list)
```

## Building The AI Trading Workflow

To build an AI trading workflow, the AI engine will ingest market data, paired with a carefully crafted system prompt. This prompt is vital for optimizing the bot’s performance, and its outputs should always be rigorously tested.

### How to Craft an AI Trade Analysis Prompt?

Start by drafting a clear, structured instruction that tells the LLM to evaluate supplied market data and deliver a formatted trade recommendation.

Prompt engineering is key here as it directly impacts how reliably the bot interprets data and makes decisions, turning a general-purpose LLM into a focused trading tool.

Here's a solid prompt template you can use or adapt. Save it in your `prompt_template.txt` for your bot to load:
```
"You are a financial analyst expert in cryptocurrency markets, skilled in technical analysis using OHLC data.

Each object you receive contains the Symbol, its price change in the last hour (in %) and its OHLC price data for the last 180 days in hourly intervals.

You receive OHLC price data in the format: {symbol: btc, coin_id:btc, prince_change:5, realized_pnl:0.0, prices: [[1758380400000, 115977.0, 116048.0, 115925.0, 116039.0], [1758384000000, 116073.0, 116154.0, 116000.0, 116011.0], [1758387600000, 116033.0, 116083.0, 115925.0, 116069.0]]} where each inner array represents [timestamp, open, high, low, close].

Analyze trends, indicators (e.g., moving averages, RSI, MACD), volatility, patterns, and recent action.

Output a recommendation: 'BUY' for upward potential, 'SELL for downward pressure, 'NEUTRAL' for mixed signals.

Your job is to try and identify an alpha, pattern breakout, or trend that indicates a strong likelihood of a price movement in the near future by analyzing the provided OHLC in context with the price change in the last hour.

Response structure MUST BE EXACTLY as follows, NO OTHER OUTPUTS. Use exactly these headings and format:

- Recommendation: BUY/SELL/NEUTRAL
- Direction: Bullish/Bearish/Sideways
- Strength: Low/Medium/High
- Summary: 1-2 sentence explanation.
- Pools: mention some of the pools for this coin. If no pools are provided in the prompt, assume no safe pools were found and warn the user.

Stick to the provided data.

Data:"
```

### How to Code an AI Trading Logic in Python?

Start by building a service that can interact with your favorite LLM, send user and system prompts, and return an output.

Create a new file under `services/openai_service.py`. Define an `OpenAIService` Class with a single method called `get_chat_completion`.
```python
from utils.load_env import openai_api_key
from openai import OpenAI

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=openai_api_key)

    def get_chat_completion(self, data, instructions: str, model="gpt-5-mini"):
        response = self.client.responses.create(
            model=model, input=str(data), instructions=instructions
        )
        return response.output_text
```

Our code now has the basic building blocks for fetching data from the CoinGecko API and passing it to OpenAI for technical analysis.

For this to be an actual trading bot, we need a service that can handle the buying and selling of cryptocurrencies.

Create a new file under `services/trading_service.py`. Since our example illustrates AI trading in a safe, paper-trading environment, we won’t connect to an exchange API, and instead just return basic order information.
```python
from datetime import datetime
from data_access.models.paper_order import PaperOrder

class TradingService:
    def __init__(self):
        pass

    @staticmethod
    def buy(symbol: str, current_price: float, quantity: float) -> PaperOrder:
        return PaperOrder(
            timestamp=datetime.now(),
            buy_price=current_price,
            quantity=quantity,
            symbol=symbol,
            direction="BUY",
        )

    @staticmethod
    def sell(symbol: str, current_price: float, quantity: float) -> PaperOrder:
        return PaperOrder(
            timestamp=datetime.now(),
            buy_price=current_price,
            quantity=quantity,
            symbol=symbol,
            direction="SELL",
        )

    @staticmethod
    def calculate_cost_basis(
        current_cost_basis: float,
        total_qty: float,
        new_order_qty: float,
        new_order_price: float,
    ) -> float:
        new_total_quantity = total_qty + new_order_qty
        if new_total_quantity == 0:
            return 0  # If all quantities are sold, cost basis resets
        return (
            (current_cost_basis * total_qty) + (new_order_price * new_order_qty)
        ) / new_total_quantity
```

We have also added a `calculate_cost_basis` method to track the position's average entry price.

### Storing Trade Data

The final missing component is a service that can store and retrieve our trading data. This will be our **Data Access Layer (DAL)**.

For this project, we will use local `.json` files, as they require minimal setup and allow us to get started quickly.

Under `data_access/DAL/` we’re going to define 4 different files:

*   `Base_JSON_DAL.py`: Base layer for reading and writing .json.
*   `coins_DAL.py`: For operations on the coin object.
*   `orders_DAL.py`: For operations on the paper_order object.
*   `portfolio_DAL.py`: For operations on portfolio_item object.

**`data_access/DAL/Base_JSON_DAL.py`**
```python
import json
import os
from typing import Callable

class Base_JSON_DAL:
    @staticmethod
    def read_data(file_path: str):
        if not os.path.exists(file_path):
            return []
        with open(file_path, "r") as f:
            data = f.read().strip()
            if not data:
                return []
            return json.loads(data)

    @staticmethod
    def write_data(file_path: str, items):
        with open(file_path, "w") as f:
            f.write(json.dumps(items, default=str))

    @staticmethod
    def insert(file_path: str, item):
        items = Base_JSON_DAL.read_data(file_path)
        items.append(item)
        Base_JSON_DAL.write_data(file_path, items)

    @staticmethod
    def get_all(file_path: str):
        return Base_JSON_DAL.read_data(file_path)

    @staticmethod
    def delete(file_path: str, match_fn: Callable):
        items = Base_JSON_DAL.read_data(file_path)
        items = [item for item in items if not match_fn(item)]
        Base_JSON_DAL.write_data(file_path, items)
```

**`data_access/DAL/coins_DAL.py`**
```python
from typing import List, Optional
from data_access.models.coin import Coin
from .Base_JSON_DAL import Base_JSON_DAL

class CoinsDAL:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_all_coins(self) -> List[Coin]:
        return Coin.from_list(Base_JSON_DAL.get_all(self.file_path))

    def get_coin_by_symbol(self, symbol: str) -> Optional[Coin]:
        return next((c for c in self.get_all_coins() if c.symbol == symbol), None)

    def update_coin_pnl(self, symbol: str, new_realized_pnl: float) -> Optional[Coin]:
        coins = self.get_all_coins()
        for coin in coins:
            if coin.symbol == symbol:
                coin.realized_pnl = new_realized_pnl
                break
        else:
            return None
        Base_JSON_DAL.write_data(self.file_path, [c.to_dict() for c in coins])
        return coin

    def add_prices_to_coin(
        self, symbol: str, prices: List[list]
    ) -> Optional[List[list]]:
        coins = self.get_all_coins()
        for coin in coins:
            if coin.symbol == symbol:
                coin.prices.extend(prices)
                Base_JSON_DAL.write_data(self.file_path, [c.to_dict() for c in coins])
                return prices
        return None

    def add_coin(
        self,
        symbol: str,
        coin_id: str,
        realized_pnl: float = 0.0,
        price_change: float = 0.0,
    ) -> Optional[Coin]:
        coins = self.get_all_coins()
        if any(c.symbol == symbol for c in coins):
            return None
        new_coin = Coin(
            symbol=symbol,
            coin_id=coin_id,
            realized_pnl=realized_pnl,
            prices=[],
            price_change=price_change,
        )
        coins.append(new_coin)
        Base_JSON_DAL.write_data(self.file_path, [c.to_dict() for c in coins])
        return new_coin

    def update_coin_price_change(
        self, symbol: str, price_change: float
    ) -> Optional[Coin]:
        coins = self.get_all_coins()
        for coin in coins:
            if coin.symbol == symbol:
                coin.price_change = price_change
                Base_JSON_DAL.write_data(self.file_path, [c.to_dict() for c in coins])
                return coin
        return None
```

**`data_access/DAL/orders_DAL.py`**
```python
from ..models.paper_order import PaperOrder
from .Base_JSON_DAL import Base_JSON_DAL
from typing import List, Literal, Optional
from datetime import datetime

class OrdersDAL:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_all_orders(
        self,
        direction: Optional[Literal["BUY", "SELL"]] = None
    ) -> List[PaperOrder]:
        orders = PaperOrder.from_list(Base_JSON_DAL.get_all(self.file_path))
        if direction:
            orders = [o for o in orders if o.direction == direction]
        return orders

    def insert_order(
        self,
        timestamp: datetime,
        buy_price: float,
        quantity: float,
        symbol: str,
        direction: str,
    ) -> PaperOrder:
        orders = self.get_all_orders()
        new_order = PaperOrder(
            timestamp=timestamp,
            buy_price=buy_price,
            quantity=quantity,
            symbol=symbol,
            direction=direction,
        )
        orders.append(new_order)
        Base_JSON_DAL.write_data(self.file_path, [o.to_dict() for o in orders])
        return new_order
```

**`data_access/DAL/portfolio_DAL.py`**
```python
from ..models.portfolio_item import PortfolioItem, PnLEntry
from .Base_JSON_DAL import Base_JSON_DAL
from typing import List, Optional
from datetime import datetime

class PortfolioDAL:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_all_portfolio_items(self) -> List[PortfolioItem]:
        return PortfolioItem.from_list(Base_JSON_DAL.get_all(self.file_path))

    def get_portfolio_item_by_symbol(self, symbol: str) -> Optional[PortfolioItem]:
        return next(
            (item for item in self.get_all_portfolio_items() if item.symbol == symbol),
            None,
        )

    def insert_portfolio_item(
        self, symbol: str, cost_basis: float, total_quantity: float
    ) -> PortfolioItem:
        items = self.get_all_portfolio_items()
        new_item = PortfolioItem(
            symbol=symbol, cost_basis=cost_basis, total_quantity=total_quantity
        )
        items.append(new_item)
        Base_JSON_DAL.write_data(self.file_path, [i.to_dict() for i in items])
        return new_item

    def update_portfolio_item_by_symbol(
        self, symbol: str, cost_basis: float, additional_quantity: float
    ) -> Optional[PortfolioItem]:
        items = self.get_all_portfolio_items()
        for item in items:
            if item.symbol == symbol:
                item.cost_basis = cost_basis
                item.total_quantity += additional_quantity
                Base_JSON_DAL.write_data(self.file_path, [i.to_dict() for i in items])
                return item
        return None

    def add_pnl_entry_by_symbol(
        self, symbol: str, date: datetime, value: float
    ) -> Optional[PnLEntry]:
        items = self.get_all_portfolio_items()
        for item in items:
            if item.symbol == symbol:
                pnl_entry = PnLEntry(date=date, value=value)
                item.pnl_entries.append(pnl_entry)
                Base_JSON_DAL.write_data(self.file_path, [i.to_dict() for i in items])
                return pnl_entry
        return None
```

### Building The Logic and Running The Trading Bot

This is where we put together all the services that we’ve built.

Create a `main.py` file at the root of your project. Inside, start by importing dependencies, defining file paths for our local .json storage, and instantiating the CoinGecko and OpenAI classes.
```python
import os
from data_access.DAL.orders_DAL import OrdersDAL
from data_access.DAL.portfolio_DAL import PortfolioDAL
from data_access.DAL.coins_DAL import CoinsDAL
from data_access.models.coin import Coin
from services.coingecko_service import CoinGecko
from services.openai_service import OpenAIService
from services.trading_service import TradingService
from workers.initializer import initialize_coin_data
from utils.load_env import *
from datetime import datetime
import time

COINS_FILE = os.path.join(os.path.dirname(__file__), "data_access/data/coins.json")
ORDERS_FILE = os.path.join(os.path.dirname(__file__), "data_access/data/orders.json")
PORTFOLIO_FILE = os.path.join(
    os.path.dirname(__file__), "data_access/data/portfolio.json"
)

# Initialize DALs
coins_dal = CoinsDAL(COINS_FILE)
orders_dal = OrdersDAL(ORDERS_FILE)
portfolio_dal = PortfolioDAL(PORTFOLIO_FILE)

# Initialize services
cg = CoinGecko()
ai = OpenAIService()
```

Next, let’s populate our local database with initial coin data.
```python
def initialize_coin_data(coins_file):
    print(f"Initializing {coins_file}...")
    if not os.path.exists(coins_file):
        with open(coins_file, "w") as f:
            f.write("[]")
    if coins_dal.get_all_coins():
        print("JSON already initialized, skipping...")
        return
    all_coins = cg.get_coins()
    for coin in all_coins:
        coins_dal.add_coin(coin.symbol, coin.coin_id)
        ohlc_data = cg.get_historic_ohlc_by_coin_id(
            coin.coin_id, days=180, interval="hourly"
        )
        coins_dal.add_prices_to_coin(coin.symbol, ohlc_data)
    print(f"Added {len(all_coins)} coins.")
    print(f"Added historical prices to {len(all_coins)} coins.")

# Populate JSON files with initial data
coins = initialize_coin_data(COINS_FILE)
```

Now let’s handle the buy logic:
```python
def handle_buy(coin: Coin, current_price: float):
    context = str(coin)
    recommendation = ai.get_chat_completion(context, prompt_template)
    if "BUY" not in recommendation:
        print(f"NOT buying {coin.symbol} as per AI recommendation: {recommendation}")
        return
    print(f" Buying {coin.symbol} as per AI recommendation: {recommendation}")
    order = TradingService.buy(coin.symbol, current_price, qty)
    existing_portfolio = portfolio_dal.get_portfolio_item_by_symbol(order.symbol)
    if existing_portfolio is None:
        portfolio_dal.insert_portfolio_item(
            order.symbol, order.buy_price, order.quantity
        )
        print(
            f"Bought {order.symbol} and inserted new portfolio item for {order.symbol}"
        )
    else:
        cost_basis = TradingService.calculate_cost_basis(
            existing_portfolio.cost_basis,
            existing_portfolio.total_quantity,
            order.quantity,
            order.buy_price,
        )
        portfolio_dal.update_portfolio_item_by_symbol(
            order.symbol, cost_basis, order.quantity
        )
        print(
            f"Bought {order.symbol}. We already hold {order.symbol}, updating existing portfolio with new order data."
        )
    orders_dal.insert_order(
        order.timestamp, order.buy_price, order.quantity, order.symbol, order.direction
    )
```

On lines 4, 5, and 6, we feed the OHLC data into our AI engine to generate a trade recommendation. Based on our prompt, the AI will return a '**BUY**', '**SELL**', or '**NEUTRAL**' signal. If the recommendation is not '**BUY**', the function exits early.

### Creating Stop Loss and Take Profit Algorithms

Next, let’s tackle the sell logic. A sell is triggered only when either the Stop Loss or Take Profit threshold is reached.
```python
def handle_sell(coin, current_price):
    buy_orders = orders_dal.get_all_orders("BUY")
    # Filter buy orders for the current symbol
    filtered_buy_orders = [order for order in buy_orders if order.symbol == coin.symbol]
    if not filtered_buy_orders:
        return
    for order in filtered_buy_orders:
        stop_loss_price = order.buy_price * (1 - sl / 100)
        take_profit_price = order.buy_price * (1 + tp / 100)
        current_pnl = (current_price - order.buy_price) / order.buy_price * 100
        if current_price <= stop_loss_price:
            sell_order = TradingService.sell(
                order.symbol, current_price, order.quantity
            )
            print(
                f"Stop Loss Triggered: Sold {order.quantity} of {order.symbol} at ${current_price}"
            )
        elif current_price >= take_profit_price:
            sell_order = TradingService.sell(
                order.symbol, current_price, order.quantity
            )
            print(
                f"Take Profit Triggered: Sold {order.quantity} of {order.symbol} at ${current_price}"
            )
        else:
            continue
        orders_dal.insert_order(
            sell_order.timestamp,
            sell_order.buy_price,
            sell_order.quantity,
            sell_order.symbol,
            sell_order.direction,
        )
        coins_dal.update_coin_pnl(order.symbol, current_pnl)
```

Finally, create an infinite loop so the bot continues to execute, look for new trade opportunities, and manage existing orders:
```python
def main():
    print("Starting up JSON data...")
    time.sleep(5)
    while True:
        coins_with_historical_data = coins_dal.get_all_coins()
        for coin in coins_with_historical_data:
            current_price = cg.get_price_by_coin_id(coin.coin_id)
            coins_dal.update_coin_price_change(coin.symbol, coin.price_change)
            handle_buy(coin, current_price)
            handle_sell(coin, current_price)
            portfolio_dal.add_pnl_entry_by_symbol(
                coin.symbol, datetime.now(), coin.prices[-1][1]
            )
            break
        print("Engine cycle complete, sleeping for 1 hour.")
        time.sleep(3600)

if __name__ == "__main__":
    main()
```

All that’s left to do now is tweak your settings and run your script.

## How to Mitigate AI Crypto Trading Risks?

Risk in AI crypto trading is managed through hard-coded rules that can override the AI’s recommendations. While AI excels at data analysis, it lacks the human judgment to account for all market nuances, making manual safeguards essential.

Key mitigation techniques include setting firm stop-loss and take-profit levels, as we've done in our **handle_sell** method, and actively filtering out scam tokens. You can also avoid potentially malicious tokens by using data from CoinGecko API to check for honeypot flags or analyze metrics like liquidity and transaction volume.

### How to Detect Scam Tokens Using CoinGecko API?

To detect scam tokens, you can use the CoinGecko API to analyze on-chain data and identify potential risks with the help of the [Megafilter](https://docs.coingecko.com/reference/pools-megafilter) or [Search Pools](https://docs.coingecko.com/reference/search-pools) endpoints.

The surge in new tokens amplifies scam risks, especially honeypots that trap investors via manipulated liquidity, plus other frauds exploiting lax oversight.

For our implementation, we’re going to use the [Search Pools](https://docs.coingecko.com/reference/search-pools) endpoint as it allows us to pass a search query, filtering by coin symbol.
```python
def check_pools(coin: Coin):
    pools = cg.search_pools(coin.symbol)
    filtered_pools = []
    for pool in pools["data"]:
        reserve = pool.get("reserve_in_usd", 0)
        volume = pool.get("volume_in_usd", {}).get("h24", 0)
        buys = pool.get("buys_24h", 0)
        if (
            reserve >= min_reserves_usd
            and volume >= min_volume_24h
            and buys >= min_buys_24h
        ):
            filtered_pools.append(pool)
    return filtered_pools
```

To add this check to your bot, simply modify the first 3 lines of your **handle_buy** function to include the new check. The AI will flag if no legitimate pools are found for your coin.
```python
safe_pools = check_pools(coin)
context = str(coin) + str(safe_pools)
recommendation = ai.get_chat_completion(context, prompt_template)
```

## How to Backtest an AI Crypto Trading Strategy?

To backtest an AI trading bot across time-series data, the AI should generate a recommendation for each data point, using the full historical context each time. If the recommendation is to buy, log the price and timestamp accordingly. Start by fetching a long period of historical OHLCV data.

Consider leveraging CoinGecko’s paid API plans for access to comprehensive data stretching back to 2013, unlocking deeper insights for your strategy. From this, you can compute the average return of the AI’s recommendations to evaluate profitability.

Here is a fully working example of a backtest for the AI trading bot that we’ve built:
```python
import os
from data_access.DAL.coins_DAL import CoinsDAL
from services.coingecko_service import CoinGecko
from services.openai_service import OpenAIService
from utils.load_env import *
from utils.load_env import prompt_template

COINS_FILE = os.path.join(os.path.dirname(__file__), "data_access/data/coins.json")
coins_dal = CoinsDAL(COINS_FILE)
ai = OpenAIService()
cg = CoinGecko()

def run_backtest_single_coin(prompt_template, symbol):
    coin = coins_dal.get_coin_by_symbol(symbol)
    if not coin:
        print(f"Coin with symbol '{symbol}' not found.")
        return []
    results = []
    buy_entries = []
    for i, price_entry in enumerate(coin.prices, start=1):
        price_slice = coin.prices[:i]
        timestamp = price_entry[0]
        close = price_entry[-1]
        recommendation = ai.get_chat_completion(price_slice, prompt_template)
        print(f"recommendation: {recommendation}")
        if "BUY" in recommendation.upper():
            buy_entries.append({"timestamp": timestamp, "buy_price": close})
        results.append(
            {
                "symbol": coin.symbol,
                "timestamp": timestamp,
                "close": close,
                "recommendation": recommendation,
            }
        )
    # Calculate PNL for each buy entry using the final price in the price list
    final_price = coin.prices[-1][-1] if coin.prices else None
    for entry in buy_entries:
        entry["final_price"] = final_price
        entry["pnl"] = (
            (final_price - entry["buy_price"]) / entry["buy_price"] * 100
            if final_price is not None
            else None
        )
    return results, buy_entries

if __name__ == "__main__":
    symbol = input("Enter coin symbol to backtest: ").strip()
    results, buy_entries = run_backtest_single_coin(prompt_template, symbol)
    print("\nAll recommendations:")
    for r in results:
        print(r)
    print("\nBuy signals and PNL:")
    for b in buy_entries:
        print(b)
```

## Can Beginners Use AI Crypto Trading Bots?

Yes, beginners can use AI crypto trading bots, especially with guides like this that break down the process into manageable steps using familiar tools like Python.

That said, while this tutorial lowers the entry barrier for building one, beginners should approach with caution, as crypto markets are volatile and unpredictable.

**Always start with paper trading to simulate strategies without financial risk, and recognize that no bot guarantees profits.**

The primary aim is to learn through experimentation in a safe setup before gaining enough confidence to transition to trading on live exchanges.

## Do AI Bots Actually Work for Crypto Trading?

AI bots can enhance crypto trading by delivering data-driven insights and automation, though their success depends heavily on implementation and the quality of the underlying market data.

They offer clear advantages, such as pivoting strategies instantly with a new prompt and processing multiple data streams for complex analysis. However, challenges like potential AI 'hallucinations' and incorrect recommendations are inevitable, so it is crucial to approach AI trading with a mindset focused on learning and continuous validation.

## Potential Future Enhancements

The current bot analyzes price and on-chain data, but you can extend its capabilities by incorporating social media or news feeds for sentiment analysis, giving the AI even more context when making trade recommendations.

Another powerful addition is a reasoning journal, where the bot logs the AI's rationale for each trade. This data can be invaluable for refining your prompts and improving strategy performance over time.

## Conclusion

In this guide, you've gained practical skills to build an AI crypto trading bot: from setting up a clean project environment, to pulling in varied market and on-chain data via the CoinGecko API, crafting effective prompts for the AI's decision-making core, adding essential risk mitigations, and sketching out a backtesting framework to validate your setup.

Remember, AI bots serve to enhance your trading approach. They are tools for augmentation, not a substitute for thoughtful strategy and oversight.

Ready to go beyond testing? Consider upgrading to a [paid API plan](https://www.coingecko.com/en/api/pricing) with access to higher rate limits and increased call credits that are necessary for running a production-level AI trading bot or conducting large-scale backtesting.

⚡️ Get started quickly by cloning this [GitHub Repository](https://github.com/CyberPunkMetalHead/ai-crypto-trading-bot).

![](https://static.coingecko.com/gecko-logo-new-color.svg)

CoinGecko's Content Editorial Guidelines