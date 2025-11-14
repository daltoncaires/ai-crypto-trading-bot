# How to Build an AI Crypto Trading Bot

 4.6



| by

  [Cryptomaton](https://www.coingecko.com/author/Cryptomaton)  |

Edited by

  [Brian Lee](https://www.coingecko.com/author/Brian%20Lee)     - Updated September 26 2025

The rapid advancement of Artificial Intelligence (AI) has introduced powerful new tools for traders. Unlike traditional rule-based bots that follow static instructions, AI-powered systems can analyze complex market data, adapt to changing conditions, and identify subtle patterns that humans might miss. This has led many traders to explore building AI crypto trading bots to gain a competitive edge.

In this step-by-step tutorial, we'll build a functional AI crypto trading bot in Python. We will use the [CoinGecko API](https://www.coingecko.com/en/api) for comprehensive market and on-chain data and an OpenAI large language model (LLM) as the decision-making core.

![How to Build an AI Crypto Trading Bot Step-by-step Guide](https://assets.coingecko.com/coingecko/public/ckeditor_assets/pictures/34052/content_Build_AI_Crypto_Trading_Bot.webp)

* * *

## What Is an AI Crypto Trading Bot?

An AI crypto trading bot is software that automates cryptocurrency trades by utilizing artificial intelligence to analyze market data and make informed decisions.

Unlike traditional algorithmic trading bots, which rely on fixed "if-then" rules, AI bots can learn from data, adapt to new conditions, and detect nuanced patterns that rigid systems might miss.

Key advantages include:

* **Dynamic logic**: AI bots can dynamically adjust strategies by modifying the prompt, thereby enhancing testing speed and reducing iteration time.
* **24/7 operation**: They run continuously without fatigue, monitoring markets around the clock.
* **No emotions**: Trades are based on analysis rather than fear or greed, reducing impulsive errors.
* **Handling complex variables**: Beyond basic indicators like RSI or MACD, they can incorporate diverse factors such as on-chain metrics, sentiment, or emerging trends for more informed strategies.

## How Does an AI Trading Bot Work?

AI trading bots work by ingesting market data and using an AI engine to evaluate it for trade opportunities, in accordance with a well-crafted user prompt.

At a high level, an AI trading bot's workflow breaks down into four main stages:

![](https://assets.coingecko.com/coingecko/public/ckeditor_assets/pictures/34049/content_flowchart.webp)

* **Data Layer**: This stage involves ingesting real-time and historical crypto data from sources like the CoinGecko API. This may include any time series data.
* **User Settings**: This includes the prompt and any specific trading instructions, such as Stop Loss and Take Profit.
* **AI Engine**: Data & prompts are ingested by the AI engine, which is typically powered by an LLM like OpenAI, to produce a recommendation.
* **Safety Checks**: Hard-coded rules like Stop Loss and Take Profit are applied, along with additional safeguards such as CoinGecko's honeypot checks to verify liquidity pool integrity and avoid scams.
* **Trade Layer**: The bot places trades based on the validated signal. For beginners, it is highly encouraged to start with paper trading to test strategies in a risk-free environment before deploying live funds on a CEX or DEX.
* **Data Access Layer (DAL)**: Trades are stored locally for reporting purposes. The trade engine regularly checks if any order may be closed in accordance with the Take Profit or Stop Loss rules.

## Prerequisites

Here’s what you’re going to need to complete this project:

* A CoinGecko API Key
* Python 3.11+
* An OpenAI API Key

### Obtaining a CoinGecko API Key

All endpoints used in this guide can be accessed with a free Demo API key. If you don’t have one, follow this guide to [get your free Demo API key](https://support.coingecko.com/hc/en-us/articles/21880397454233-User-Guide-How-to-sign-up-for-CoinGecko-Demo-API-and-generate-an-API-key).

AI trading bots may make frequent data requests, and can cause the Demo plan's rate limits to be exhausted quickly. For production use or intensive backtesting, upgrading to a paid plan is recommended.

[![Subscribe to CoinGecko API](https://assets.coingecko.com/coingecko/public/ckeditor_assets/pictures/34010/content_Subcribe_to_CoinGecko_API_CTA_-_DEX.webp)](https://www.coingecko.com/en/api/pricing)

For this project, we’ll be using the following CoinGecko API endpoints:

* [Coin Price by IDs](https://docs.coingecko.com/reference/simple-price)
* [Coin OHLC Chart by ID](https://docs.coingecko.com/reference/coins-id-ohlc)
* [Coins List with Market Data](https://docs.coingecko.com/reference/coins-markets)
* [Search Pools](https://docs.coingecko.com/reference/search-pools)

### Obtaining an OpenAI API Key

To obtain an OpenAI API key, log in to your OpenAI account and navigate to API Keys under Organization.

Click **+Create New Secret Key** in the top right corner and copy the key.

### Setting Up The Project Environment

To get started, create a new directory for your project:

mkdir ai-crypto-bot

cd ai-crypto-bot

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/dir.sh)   [dir.sh](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-dir-sh) hosted with ❤ by [GitHub](https://github.com)

Next, set up a Python virtual environment to isolate your project's dependencies:

python -m venv env

# Activate on Windows

env\\Scripts\\activate

# On Linux/Mac

source env/bin/activate

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/env.sh)   [env.sh](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-env-sh) hosted with ❤ by [GitHub](https://github.com)

### Installing Dependencies

Install the required packages by creating a requirements.txt file in the project root with the following content:

annotated-types\==0.7.0

anyio\==4.10.0

certifi\==2025.8.3

charset-normalizer\==3.4.3

colorama\==0.4.6

dataclass-wizard\==0.35.1

distro\==1.9.0

h11\==0.16.0

httpcore\==1.0.9

httpx\==0.28.1

idna\==3.10

jiter\==0.11.0

openai\==1.108.1

pydantic\==2.11.9

pydantic\_core\==2.33.2

python-dotenv\==1.1.1

requests\==2.32.5

sniffio\==1.3.1

tqdm\==4.67.1

typing-inspection\==0.4.1

typing\_extensions\==4.15.0

tzdata\==2025.2

urllib3\==2.5.0

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/requirements.txt)   [requirements.txt](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-requirements-txt) hosted with ❤ by [GitHub](https://github.com)

Now install them by running:

pip install -r requirements.txt

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/install.sh)   [install.sh](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-install-sh) hosted with ❤ by [GitHub](https://github.com)

### Storing Credentials and Settings

Create a **.env** file in the project root to store API keys and trading configuration.

Copy this template:

CG\_API\_KEY \= "CG-API-KEY"

OPENAI\_API\_KEY\="sk-OPENAI-API-KEY"

# Application Settings

TAKE\_PROFIT \= "20"

STOP\_LOSS \= "10"

ORDER\_AMOUNT \= "50"

PRICE\_CHANGE \= "3"

# Pool Safety Checks

MIN\_VOLUME\_24H \= "1000000"

MIN\_RESERVES\_USD\="1000000"

MIN\_BUYS\_24H \= "1000"

# Prompt Settings

PROMPT\_TEMPLATE \= ./prompt\_template.txt

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/.env)   [.env](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-env) hosted with ❤ by [GitHub](https://github.com)

Replace the placeholder API keys with your actual CoinGecko API key and OpenAI API key.

Here's what each setting does:

* **TAKE\_PROFIT:** The percentage gain threshold to sell and lock in profits (e.g., 20% above entry price).
* **STOP\_LOSS:** The percentage loss threshold to sell and cut losses (e.g., 10% below entry price).
* **ORDER\_AMOUNT**: The fixed USD amount to allocate per trade.
* **MIN\_VOLUME\_24H**: Minimum trading volume (in USD) for a pool to qualify as safe.
* **MIN\_RESERVES\_USD**: Minimum liquidity reserves (in USD) to filter out low-liquidity pools.
* **MIN\_BUYS\_24H**: Minimum number of buys in the last 24 hours to indicate genuine activity.
* **PROMPT\_TEMPLATE**: Path to the file containing the AI prompt template.

Create a **prompt\_template.txt** file in your project root. We will store our system prompt in this separate file, which will be referenced in our .env file. We will define the prompt's content later in the guide.

To load your config, create a new file under **/utils/load\_env.py**:

import os

from dotenv import load\_dotenv

load\_dotenv()

cg\_api\_key \= os.getenv("CG\_API\_KEY")

openai\_api\_key \= os.getenv("OPENAI\_API\_KEY")

prompt\_template \= open(os.getenv("PROMPT\_TEMPLATE"), "r").read()

\# Trade Settingd

tp \= float(os.getenv("TAKE\_PROFIT"))

sl \= float(os.getenv("STOP\_LOSS"))

qty \= float(os.getenv("ORDER\_AMOUNT"))

price\_change \= float(os.getenv("PRICE\_CHANGE"))

\# Pool Safety Checks

min\_volume\_24h \= float(os.getenv("MIN\_VOLUME\_24H"))

min\_reserves\_usd \= float(os.getenv("MIN\_RESERVES\_USD"))

min\_buys\_24h \= float(os.getenv("MIN\_BUYS\_24H"))

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/load_env.py)   [load\_env.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-load_env-py) hosted with ❤ by [GitHub](https://github.com)

## How to Feed Real-time & Historical Crypto Market Data to AI?

You can feed real-time and historical crypto market data to an AI trading from a comprehensive data source like the CoinGecko API. This data is crucial for the AI to perform its analysis. The CoinGecko API provides a wide range of data points, including real-time prices, historical OHLC (Open, High, Low, Close) candlestick data, market cap, and liquidity data, which are essential for building a robust trading strategy.

### Fetching Data: How to Get Historical Data for Major Coins?

Under **/services/services/coingecko\_service.py**, we’re going to define a **CoinGecko** class, with a method for each endpoint.

Start by importing the required dependencies and define the constructor to include the CoinGecko authentication headers. Don’t worry about any types that you have not yet defined.

import requests

from data\_access.models.coin import Coin

from utils.load\_env import \*

from typing import List

from datetime import datetime

class CoinGecko:

 def \_\_init\_\_(self):

 self.root \= "https://pro-api.coingecko.com/api/v3"

 self.headers \= {

 "accept": "application/json",

 "x-cg-pro-api-key": f"{cg\_api\_key}",

}

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/coingecko_service_init.py)   [coingecko\_service\_init.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-coingecko_service_init-py) hosted with ❤ by [GitHub](https://github.com)

Note: If you’re using the Demo API, you’ll need to change the self.root URL to **https://api.coingecko.com/api/v3** and update the **self.headers** key to **x-cg-demo-api-key**.

Next, add a new method to the class to fetch OHLC data by coin ID:

 def get\_historic\_ohlc\_by\_coin\_id(

 self,

 coin\_id: str,

 vs\_currency: str \= "usd",

 days: int \= 1,

 interval: str \= "hourly",

):

 request\_url \= f"{self.root}/coins/{coin\_id}/ohlc?vs\_currency={vs\_currency}&days={days}&interval={interval}"

 response \= requests.get(request\_url, headers\=self.headers)

 candles \= response.json()

 return candles

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/coingecko_service_ohlc.py)   [coingecko\_service\_ohlc.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-coingecko_service_ohlc-py) hosted with ❤ by [GitHub](https://github.com)

💡 **Pro tip**: The coin ID is a unique identifier for each cryptocurrency and may not always match the coin's ticker symbol. You can find the complete list of coin IDs via the [/coins/list](https://docs.coingecko.com/reference/coins-list) endpoint or by referencing [this spreadsheet](https://docs.google.com/spreadsheets/d/1wTTuxXt8n9q7C4NDXqQpI3wpKu1_5bGVmP9Xz0XGSyU/edit?usp=sharing).

To run this, instantiate the class and call the method with the desired parameters:

cg \= CoinGecko()

print(cg.get\_historic\_ohlc\_by\_coin\_id("bitcoin", "usd", days\=180, interval\="daily"))

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/coingecko_service_ohlc_example.py)   [coingecko\_service\_ohlc\_example.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-coingecko_service_ohlc_example-py) hosted with ❤ by [GitHub](https://github.com)

This will return raw candlestick data, along with a timestamp for search entry:

\[

{

 "coinId": "bitcoin",

 "symbol": "btc",

 "realizedPnl": 0.0,

 "priceChange": \-0.10940523691445969,

 "prices": \[

\[1758380400000, 115977.0, 116048.0, 115925.0, 116039.0\],

\[1758384000000, 116073.0, 116154.0, 116000.0, 116011.0\],

\[1758387600000, 116033.0, 116083.0, 115925.0, 116069.0\]

\],

\[...\]

},

{...}

\]

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/data.json)   [data.json](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-data-json) hosted with ❤ by [GitHub](https://github.com)

Continue by creating methods for the remaining CoinGecko endpoints, and nest them under the **CoinGecko** class.

The following methods will enable our AI crypto trading bot to fetch real-time prices, identify promising large caps, and find safe liquidity pools:

 def get\_price\_by\_coin\_id(self, coin\_id: str):

 request\_url \= self.root + f"/simple/price?ids={coin\_id}&vs\_currencies=usd"

 response \= requests.get(request\_url, self.headers)

 data \= response.json()

 return data.get(coin\_id, {}).get("usd")

 def get\_coins(self) \-> List\[Coin\]:

 request\_url \= (

 self.root

 + "/coins/markets?order=market\_cap\_desc&per\_page=250&vs\_currency=usd&price\_change\_percentage=1h"

)

 response \= requests.get(request\_url, headers\=self.headers)

 data \= response.json()

 coins \= \[\]

 now \= datetime.now().timestamp()

 for coin\_data in data:

 coin \= Coin(

 coin\_id\=coin\_data\["id"\],

 symbol\=coin\_data\["symbol"\],

 realized\_pnl\=0.0,

 price\_change\=coin\_data.get(

 "price\_change\_percentage\_1h\_in\_currency", 0.0

),

)

 coin.prices \= \[\[now, coin\_data\["current\_price"\]\]\]

 coins.append(coin)

 return coins

 def search\_pools(self, query: str \= None, chain: str \= None):

 request\_url \= f"{self.root}/onchain/search/pools?query={query}"

 response \= requests.get(request\_url, headers\=self.headers)

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/coingecko_service_remaining_funcs.py)   [coingecko\_service\_remaining\_funcs.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-coingecko_service_remaining_funcs-py) hosted with ❤ by [GitHub](https://github.com)

### Defining Data

Under **/data\_access/models/**, we’re going to define the three main object types that we’ll be working with: **Coin**, **PaperOrder**, and **PortfolioItem**

**\[...\]/coin.py:**

from dataclasses import dataclass, field

from typing import List

from dataclass\_wizard import JSONWizard

@dataclass

class Coin(JSONWizard):

 coin\_id: str

 symbol: str

 realized\_pnl: float \= 0.0

 price\_change: float \= 0.0

 prices: List\[list\] \= field(default\_factory\=list)

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/coin.py)   [coin.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-coin-py) hosted with ❤ by [GitHub](https://github.com)

**\[...\]/paper\_order.py**

from typing import Literal

from dataclasses import dataclass

from datetime import datetime

from dataclass\_wizard import JSONWizard

@dataclass

class PaperOrder(JSONWizard):

 timestamp: datetime

 buy\_price: float

 quantity: float

 symbol: str

 direction: Literal\["BUY", "SELL"\]

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/paper_order.py)   [paper\_order.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-paper_order-py) hosted with ❤ by [GitHub](https://github.com)

**\[...\]/portfolio\_item.py**

from dataclasses import dataclass, field

from typing import List

from datetime import datetime

from dataclass\_wizard import JSONWizard

@dataclass

class PnLEntry(JSONWizard):

 date: datetime

 value: float

@dataclass

class PortfolioItem(JSONWizard):

 cost\_basis: float

 total\_quantity: float

 symbol: str

 pnl\_entries: List\[PnLEntry\] \= field(default\_factory\=list)

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/portfolio_item.py)   [portfolio\_item.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-portfolio_item-py) hosted with ❤ by [GitHub](https://github.com)

## Building The AI Trading Workflow

To build an AI trading workflow, the AI engine will ingest market data, paired with a carefully crafted system prompt. This prompt is vital for optimizing the bot’s performance, and its outputs should always be rigorously tested.

### How to Craft an AI Trade Analysis Prompt?

Start by drafting a clear, structured instruction that tells the LLM to evaluate supplied market data and deliver a formatted trade recommendation.

Prompt engineering is key here as it directly impacts how reliably the bot interprets data and makes decisions, turning a general-purpose LLM into a focused trading tool.

Here's a solid prompt template you can use or adapt. Save it in your **prompt\_template.txt** for your bot to load:

"You are a financial analyst expert in cryptocurrency markets, skilled in technical analysis using OHLC data.

Each object you receive contains the Symbol, its price change in the last hour (in %) and its OHLC price data for the last 180 days in hourly intervals.

You receive OHLC price data in the format: {symbol: btc, coin\_id:btc, prince\_change:5, realized\_pnl:0.0, prices: \[\[1758380400000, 115977.0, 116048.0, 115925.0, 116039.0\], \[1758384000000, 116073.0, 116154.0, 116000.0, 116011.0\], \[1758387600000, 116033.0, 116083.0, 115925.0, 116069.0\]\]} where each inner array represents \[timestamp, open, high, low, close\].

Analyze trends, indicators (e.g., moving averages, RSI, MACD), volatility, patterns, and recent action.

Output a recommendation: 'BUY' for upward potential, 'SELL for downward pressure, 'NEUTRAL' for mixed signals.

Your job is to try and identify an alpha, pattern breakout, or trend that indicates a strong likelihood of a price movement in the near future by analyzing the provided OHLC in context with the price change in the last hour.

Response structure MUST BE EXACTLY as follows, NO OTHER OUTPUTS. Use exactly these headings and format:

\- Recommendation: BUY/SELL/NEUTRAL

\- Direction: Bullish/Bearish/Sideways

\- Strength: Low/Medium/High

\- Summary: 1-2 sentence explanation.

\- Pools: mention some of the pools for this coin. If no pools are provided in the prompt, assume no safe pools were found and warn the user.

Stick to the provided data.

Data:"

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/prompt_template.txt)   [prompt\_template.txt](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-prompt_template-txt) hosted with ❤ by [GitHub](https://github.com)

### How to Code an AI Trading Logic in Python?

Start by building a service that can interact with your favorite LLM, send user and system prompts, and return an output.

Create a new file under **/services/openai\_service.py**. Define an OpenAI Class with a single method called **get\_chat\_completion**.

from utils.load\_env import openai\_api\_key

from openai import OpenAI

class OpenAIService:

 def \_\_init\_\_(self):

 self.client \= OpenAI(api\_key\=openai\_api\_key)

 def get\_chat\_completion(self, data, instructions: str, model\="gpt-5-mini"):

 response \= self.client.responses.create(

 model\=model, input\=str(data), instructions\=instructions

)

 return response.output\_text

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/openai_service.py)   [openai\_service.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-openai_service-py) hosted with ❤ by [GitHub](https://github.com)

Our code now has the basic building blocks for fetching data from the CoinGecko API and passing it to OpenAI for technical analysis.

For this to be an actual trading bot, we need a service that can handle the buying and selling of cryptocurrencies.

Create a new file under **/services/trading\_service.py**. Since our example illustrates AI trading in a safe, paper-trading environment, we won’t connect to an exchange API, and instead just return basic order information.

from datetime import datetime

from data\_access.models.paper\_order import PaperOrder

class TradingService:

 def \_\_init\_\_(self):

 pass

 @staticmethod

 def buy(symbol: str, current\_price: float, quantity: float) \-> PaperOrder:

 return PaperOrder(

 timestamp\=datetime.now(),

 buy\_price\=current\_price,

 quantity\=quantity,

 symbol\=symbol,

 direction\="BUY",

)

 @staticmethod

 def sell(symbol: str, current\_price: float, quantity: float) \-> PaperOrder:

 return PaperOrder(

 timestamp\=datetime.now(),

 buy\_price\=current\_price,

 quantity\=quantity,

 symbol\=symbol,

 direction\="SELL",

)

 @staticmethod

 def calculate\_cost\_basis(

 current\_cost\_basis: float,

 total\_qty: float,

 new\_order\_qty: float,

 new\_order\_price: float,

) \-> float:

 new\_total\_quantity \= total\_qty + new\_order\_qty

 if new\_total\_quantity \== 0:

 return 0  \# If all quantities are sold, cost basis resets

 return (

(current\_cost\_basis \* total\_qty) + (new\_order\_price \* new\_order\_qty)

) / new\_total\_quantity

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/trading_service.py)   [trading\_service.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-trading_service-py) hosted with ❤ by [GitHub](https://github.com)

We have also added a **calculate\_cost\_basis** method to track the position's average entry price.

### Storing Trade Data

The final missing component is a service that can store and retrieve our trading data. This will be our **Data Access Layer (DAL)**.

For this project, we will use local **.json** files, as they require minimal setup and allow us to get started quickly.

Under **/data\_access/DAL/** we’re going to define 4 different files:

* **Base\_JSON\_DAL.py**: Base layer for reading and writing .json.
* **coins\_DAL.py**: For operations on the coin object.
* **orders\_DAL.py**: For operations on the paper\_order object.
* **portfolio\_DAL.py**: For operations on portfolio\_item object.

**\[...\]/base\_JSON\_DAL.py**

import json

import os

from typing import Callable

class Base\_JSON\_DAL:

 @staticmethod

 def read\_data(file\_path: str):

 if not os.path.exists(file\_path):

 return \[\]

 with open(file\_path, "r") as f:

 data \= f.read().strip()

 if not data:

 return \[\]

 return json.loads(data)

 @staticmethod

 def write\_data(file\_path: str, items):

 with open(file\_path, "w") as f:

 f.write(json.dumps(items, default\=str))

 @staticmethod

 def insert(file\_path: str, item):

 items \= Base\_JSON\_DAL.read\_data(file\_path)

 items.append(item)

 Base\_JSON\_DAL.write\_data(file\_path, items)

 @staticmethod

 def get\_all(file\_path: str):

 return Base\_JSON\_DAL.read\_data(file\_path)

 @staticmethod

 def delete(file\_path: str, match\_fn: Callable):

 items \= Base\_JSON\_DAL.read\_data(file\_path)

 items \= \[item for item in items if not match\_fn(item)\]

 Base\_JSON\_DAL.write\_data(file\_path, items)

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/Base_JSON_DAL.py)   [Base\_JSON\_DAL.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-base_json_dal-py) hosted with ❤ by [GitHub](https://github.com)

**\[...\]/coins\_DAL.py**

from typing import List, Optional

from data\_access.models.coin import Coin

from .Base\_JSON\_DAL import Base\_JSON\_DAL

class CoinsDAL:

 def \_\_init\_\_(self, file\_path: str):

 self.file\_path \= file\_path

 def get\_all\_coins(self) \-> List\[Coin\]:

 return Coin.from\_list(Base\_JSON\_DAL.get\_all(self.file\_path))

 def get\_coin\_by\_symbol(self, symbol: str) \-> Optional\[Coin\]:

 return next((c for c in self.get\_all\_coins() if c.symbol \== symbol), None)

 def update\_coin\_pnl(self, symbol: str, new\_realized\_pnl: float) \-> Optional\[Coin\]:

 coins \= self.get\_all\_coins()

 for coin in coins:

 if coin.symbol \== symbol:

 coin.realized\_pnl \= new\_realized\_pnl

 break

 else:

 return None

 Base\_JSON\_DAL.write\_data(self.file\_path, \[c.to\_dict() for c in coins\])

 return coin

 def add\_prices\_to\_coin(

 self, symbol: str, prices: List\[list\]

) \-> Optional\[List\[list\]\]:

 coins \= self.get\_all\_coins()

 for coin in coins:

 if coin.symbol \== symbol:

 coin.prices.extend(prices)

 Base\_JSON\_DAL.write\_data(self.file\_path, \[c.to\_dict() for c in coins\])

 return prices

 return None

 def add\_coin(

 self,

 symbol: str,

 coin\_id: str,

 realized\_pnl: float \= 0.0,

 price\_change: float \= 0.0,

) \-> Optional\[Coin\]:

 coins \= self.get\_all\_coins()

 if any(c.symbol \== symbol for c in coins):

 return None

 new\_coin \= Coin(

 symbol\=symbol,

 coin\_id\=coin\_id,

 realized\_pnl\=realized\_pnl,

 prices\=\[\],

 price\_change\=price\_change,

)

 coins.append(new\_coin)

 Base\_JSON\_DAL.write\_data(self.file\_path, \[c.to\_dict() for c in coins\])

 return new\_coin

 def update\_coin\_price\_change(

 self, symbol: str, price\_change: float

) \-> Optional\[Coin\]:

 coins \= self.get\_all\_coins()

 for coin in coins:

 if coin.symbol \== symbol:

 coin.price\_change \= price\_change

 Base\_JSON\_DAL.write\_data(self.file\_path, \[c.to\_dict() for c in coins\])

 return coin

 return None

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/coins_DAL.py)   [coins\_DAL.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-coins_dal-py) hosted with ❤ by [GitHub](https://github.com)

**\[...\]/orders\_DAL.py**

from ..models.paper\_order import PaperOrder

from .Base\_JSON\_DAL import Base\_JSON\_DAL

from typing import List, Literal, Optional

from datetime import datetime

class OrdersDAL:

 def \_\_init\_\_(self, file\_path: str):

 self.file\_path \= file\_path

 def get\_all\_orders(

 self, direction: Optional\[Literal\["BUY", "SELL"\]\] \= None

) \-> List\[PaperOrder\]:

 orders \= PaperOrder.from\_list(Base\_JSON\_DAL.get\_all(self.file\_path))

 if direction:

 orders \= \[o for o in orders if o.direction \== direction\]

 return orders

 def insert\_order(

 self,

 timestamp: datetime,

 buy\_price: float,

 quantity: float,

 symbol: str,

 direction: str,

) \-> PaperOrder:

 orders \= self.get\_all\_orders()

 new\_order \= PaperOrder(

 timestamp\=timestamp,

 buy\_price\=buy\_price,

 quantity\=quantity,

 symbol\=symbol,

 direction\=direction,

)

 orders.append(new\_order)

 Base\_JSON\_DAL.write\_data(self.file\_path, \[o.to\_dict() for o in orders\])

 return new\_order

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/orders_DAL.py)   [orders\_DAL.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-orders_dal-py) hosted with ❤ by [GitHub](https://github.com)

**\[...\]/portfolio\_DAL.py**

from ..models.portfolio\_item import PortfolioItem, PnLEntry

from .Base\_JSON\_DAL import Base\_JSON\_DAL

from typing import List, Optional

from datetime import datetime

class PortfolioDAL:

 def \_\_init\_\_(self, file\_path: str):

 self.file\_path \= file\_path

 def get\_all\_portfolio\_items(self) \-> List\[PortfolioItem\]:

 return PortfolioItem.from\_list(Base\_JSON\_DAL.get\_all(self.file\_path))

 def get\_portfolio\_item\_by\_symbol(self, symbol: str) \-> Optional\[PortfolioItem\]:

 return next(

(item for item in self.get\_all\_portfolio\_items() if item.symbol \== symbol),

 None,

)

 def insert\_portfolio\_item(

 self, symbol: str, cost\_basis: float, total\_quantity: float

) \-> PortfolioItem:

 items \= self.get\_all\_portfolio\_items()

 new\_item \= PortfolioItem(

 symbol\=symbol, cost\_basis\=cost\_basis, total\_quantity\=total\_quantity

)

 items.append(new\_item)

 Base\_JSON\_DAL.write\_data(self.file\_path, \[i.to\_dict() for i in items\])

 return new\_item

 def update\_portfolio\_item\_by\_symbol(

 self, symbol: str, cost\_basis: float, additional\_quantity: float

) \-> Optional\[PortfolioItem\]:

 items \= self.get\_all\_portfolio\_items()

 for item in items:

 if item.symbol \== symbol:

 item.cost\_basis \= cost\_basis

 item.total\_quantity += additional\_quantity

 Base\_JSON\_DAL.write\_data(self.file\_path, \[i.to\_dict() for i in items\])

 return item

 return None

 def add\_pnl\_entry\_by\_symbol(

 self, symbol: str, date: datetime, value: float

) \-> Optional\[PnLEntry\]:

 items \= self.get\_all\_portfolio\_items()

 for item in items:

 if item.symbol \== symbol:

 pnl\_entry \= PnLEntry(date\=date, value\=value)

 item.pnl\_entries.append(pnl\_entry)

 Base\_JSON\_DAL.write\_data(self.file\_path, \[i.to\_dict() for i in items\])

 return pnl\_entry

 return None

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/portfolio_DAL.py)   [portfolio\_DAL.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-portfolio_dal-py) hosted with ❤ by [GitHub](https://github.com)

### Building The Logic and Running The Trading Bot

This is where we put together all the services that we’ve built.

Create a **main.py** file at the root of your project. Inside, start by importing dependencies, defining file paths for our local .json storage, and instantiating the CoinGecko and OpenAI classes.

import os

from data\_access.DAL.orders\_DAL import OrdersDAL

from data\_access.DAL.portfolio\_DAL import PortfolioDAL

from data\_access.DAL.coins\_DAL import CoinsDAL

from data\_access.models.coin import Coin

from services.coingecko\_service import CoinGecko

from services.openai\_service import OpenAIService

from services.trading\_service import TradingService

from workers.initializer import initialize\_coin\_data

from utils.load\_env import \*

from datetime import datetime

import time

COINS\_FILE \= os.path.join(os.path.dirname(\_\_file\_\_), "data\_access/data/coins.json")

ORDERS\_FILE \= os.path.join(os.path.dirname(\_\_file\_\_), "data\_access/data/orders.json")

PORTFOLIO\_FILE \= os.path.join(

 os.path.dirname(\_\_file\_\_), "data\_access/data/portfolio.json"

)

\# Initialize DALs

coins\_dal \= CoinsDAL(COINS\_FILE)

orders\_dal \= OrdersDAL(ORDERS\_FILE)

portfolio\_dal \= PortfolioDAL(PORTFOLIO\_FILE)

\# Initialize services

cg \= CoinGecko()

ai \= OpenAIService()

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/main_imports.py)   [main\_imports.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-main_imports-py) hosted with ❤ by [GitHub](https://github.com)

Next, let’s populate our local database with initial coin data.

def initialize\_coin\_data(coins\_file):

 print(f"Initializing {coins\_file}...")

 if not os.path.exists(coins\_file):

 with open(coins\_file, "w") as f:

 f.write("\[\]")

 if coins\_dal.get\_all\_coins():

 print("JSON already initialized, skipping...")

 return

 all\_coins \= cg.get\_coins()

 for coin in all\_coins:

 coins\_dal.add\_coin(coin.symbol, coin.coin\_id)

 ohlc\_data \= cg.get\_historic\_ohlc\_by\_coin\_id(

 coin.coin\_id, days\=180, interval\="hourly"

)

 coins\_dal.add\_prices\_to\_coin(coin.symbol, ohlc\_data)

 print(f"Added {len(all\_coins)} coins.")

 print(f"Added historical prices to {len(all\_coins)} coins.")

\# Populate JSON files with initial data

coins \= initialize\_coin\_data(COINS\_FILE)

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/main_seed.py)   [main\_seed.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-main_seed-py) hosted with ❤ by [GitHub](https://github.com)

Now let’s handle the buy logic:

def handle\_buy(coin: Coin, current\_price: float):

 context \= str(coin)

 recommendation \= ai.get\_chat\_completion(context, prompt\_template)

 if "BUY" not in recommendation:

 print(f"NOT buying {coin.symbol} as per AI recommendation: {recommendation}")

 return

 print(f" Buying {coin.symbol} as per AI recommendation: {recommendation}")

 order \= TradingService.buy(coin.symbol, current\_price, qty)

 existing\_portfolio \= portfolio\_dal.get\_portfolio\_item\_by\_symbol(order.symbol)

 if existing\_portfolio is None:

 portfolio\_dal.insert\_portfolio\_item(

 order.symbol, order.buy\_price, order.quantity

)

 print(

 f"Bought {order.symbol} and inserted new portfolio item for {order.symbol}"

)

 else:

 cost\_basis \= TradingService.calculate\_cost\_basis(

 existing\_portfolio.cost\_basis,

 existing\_portfolio.total\_quantity,

 order.quantity,

 order.buy\_price,

)

 portfolio\_dal.update\_portfolio\_item\_by\_symbol(

 order.symbol, cost\_basis, order.quantity

)

 print(

 f"Bought {order.symbol}. We already hold {order.symbol}, updating existing portfolio with new order data."

)

 orders\_dal.insert\_order(

 order.timestamp, order.buy\_price, order.quantity, order.symbol, order.direction

)

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/main_buy.py)   [main\_buy.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-main_buy-py) hosted with ❤ by [GitHub](https://github.com)

On lines 4, 5, and 6, we feed the OHLC data into our AI engine to generate a trade recommendation. Based on our prompt, the AI will return a '**BUY**', '**SELL**', or '**NEUTRAL**' signal. If the recommendation is not '**BUY**', the function exits early.

### Creating Stop Loss and Take Profit Algorithms

Next, let’s tackle the sell logic. A sell is triggered only when either the Stop Loss or Take Profit threshold is reached.

def handle\_sell(coin, current\_price):

 buy\_orders \= orders\_dal.get\_all\_orders("BUY")

 \# Filter buy orders for the current symbol

 filtered\_buy\_orders \= \[order for order in buy\_orders if order.symbol \== coin.symbol\]

 if not filtered\_buy\_orders:

 return

 for order in filtered\_buy\_orders:

 stop\_loss\_price \= order.buy\_price \* (1 \- sl / 100)

 take\_profit\_price \= order.buy\_price \* (1 + tp / 100)

 current\_pnl \= (current\_price \- order.buy\_price) / order.buy\_price \* 100

 if current\_price <= stop\_loss\_price:

 sell\_order \= TradingService.sell(

 order.symbol, current\_price, order.quantity

)

 print(

 f"Stop Loss Triggered: Sold {order.quantity} of {order.symbol} at ${current\_price}"

)

 elif current\_price \>= take\_profit\_price:

 sell\_order \= TradingService.sell(

 order.symbol, current\_price, order.quantity

)

 print(

 f"Take Profit Triggered: Sold {order.quantity} of {order.symbol} at ${current\_price}"

)

 else:

 continue

 orders\_dal.insert\_order(

 sell\_order.timestamp,

 sell\_order.buy\_price,

 sell\_order.quantity,

 sell\_order.symbol,

 sell\_order.direction,

)

 coins\_dal.update\_coin\_pnl(order.symbol, current\_pnl)

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/main_sell.py)   [main\_sell.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-main_sell-py) hosted with ❤ by [GitHub](https://github.com)

Finally, create an infinite loop so the bot continues to execute, look for new trade opportunities, and manage existing orders:

def main():

 print("Starting up JSON data...")

 time.sleep(5)

 while True:

 coins\_with\_historical\_data \= coins\_dal.get\_all\_coins()

 for coin in coins\_with\_historical\_data:

 current\_price \= cg.get\_price\_by\_coin\_id(coin.coin\_id)

 coins\_dal.update\_coin\_price\_change(coin.symbol, coin.price\_change)

 handle\_buy(coin, current\_price)

 handle\_sell(coin, current\_price)

 portfolio\_dal.add\_pnl\_entry\_by\_symbol(

 coin.symbol, datetime.now(), coin.prices\[\-1\]\[1\]

)

 break

 print("Engine cycle complete, sleeping for 1 hour.")

 time.sleep(3600)

if \_\_name\_\_ \== "\_\_main\_\_":

 main()

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/main_run.py)   [main\_run.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-main_run-py) hosted with ❤ by [GitHub](https://github.com)

All that’s left to do now is tweak your settings and run your script.

## How to Mitigate AI Crypto Trading Risks?

Risk in AI crypto trading is managed through hard-coded rules that can override the AI’s recommendations. While AI excels at data analysis, it lacks the human judgment to account for all market nuances, making manual safeguards essential.

Key mitigation techniques include setting firm stop-loss and take-profit levels, as we've done in our **handle\_sell** method, and actively filtering out scam tokens. You can also avoid potentially malicious tokens by using data from CoinGecko API to check for honeypot flags or analyze metrics like liquidity and transaction volume.

### How to Detect Scam Tokens Using CoinGecko API?

To detect scam tokens, you can use the CoinGecko API to analyze on-chain data and identify potential risks with the help of the [Megafilter](https://docs.coingecko.com/reference/pools-megafilter) or [Search Pools](https://docs.coingecko.com/reference/search-pools) endpoints.

The surge in new tokens amplifies scam risks, especially honeypots that trap investors via manipulated liquidity, plus other frauds exploiting lax oversight.

For our implementation, we’re going to use the [Search Pools](https://docs.coingecko.com/reference/search-pools) endpoint as it allows us to pass a search query, filtering by coin symbol.

def check\_pools(coin: Coin):

 pools \= cg.search\_pools(coin.symbol)

 filtered\_pools \= \[\]

 for pool in pools\["data"\]:

 reserve \= pool.get("reserve\_in\_usd", 0)

 volume \= pool.get("volume\_in\_usd", {}).get("h24", 0)

 buys \= pool.get("buys\_24h", 0)

 if (

 reserve \>= min\_reserves\_usd

 and volume \>= min\_volume\_24h

 and buys \>= min\_buys\_24h

):

 filtered\_pools.append(pool)

 return filtered\_pools

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/main_pools.py)   [main\_pools.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-main_pools-py) hosted with ❤ by [GitHub](https://github.com)

To add this check to your bot, simply modify the first 3 lines of your **handle\_buy** function to include the new check. The AI will flag if no legitimate pools are found for your coin.

 safe\_pools \= check\_pools(coin)

 context \= str(coin) + str(safe\_pools)

 recommendation \= ai.get\_chat\_completion(context, prompt\_template)

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/main_pools_implemented.py)   [main\_pools\_implemented.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-main_pools_implemented-py) hosted with ❤ by [GitHub](https://github.com)

## How to Backtest an AI Crypto Trading Strategy?

To backtest an AI trading bot across time-series data, the AI should generate a recommendation for each data point, using the full historical context each time. If the recommendation is to buy, log the price and timestamp accordingly. Start by fetching a long period of historical OHLCV data.

Consider leveraging CoinGecko’s paid API plans for access to comprehensive data stretching back to 2013, unlocking deeper insights for your strategy. From this, you can compute the average return of the AI’s recommendations to evaluate profitability.

Here is a fully working example of a backtest for the AI trading bot that we’ve built:

import os

from data\_access.DAL.coins\_DAL import CoinsDAL

from services.coingecko\_service import CoinGecko

from services.openai\_service import OpenAIService

from utils.load\_env import \*

from utils.load\_env import prompt\_template

COINS\_FILE \= os.path.join(os.path.dirname(\_\_file\_\_), "data\_access/data/coins.json")

coins\_dal \= CoinsDAL(COINS\_FILE)

ai \= OpenAIService()

cg \= CoinGecko()

def run\_backtest\_single\_coin(prompt\_template, symbol):

 coin \= coins\_dal.get\_coin\_by\_symbol(symbol)

 if not coin:

 print(f"Coin with symbol '{symbol}' not found.")

 return \[\]

 results \= \[\]

 buy\_entries \= \[\]

 for i, price\_entry in enumerate(coin.prices, start\=1):

 price\_slice \= coin.prices\[:i\]

 timestamp \= price\_entry\[0\]

 close \= price\_entry\[\-1\]

 recommendation \= ai.get\_chat\_completion(price\_slice, prompt\_template)

 print(f"recommendation: {recommendation}")

 if "BUY" in recommendation.upper():

 buy\_entries.append({"timestamp": timestamp, "buy\_price": close})

 results.append(

{

 "symbol": coin.symbol,

 "timestamp": timestamp,

 "close": close,

 "recommendation": recommendation,

}

)

 \# Calculate PNL for each buy entry using the final price in the price list

 final\_price \= coin.prices\[\-1\]\[\-1\] if coin.prices else None

 for entry in buy\_entries:

 entry\["final\_price"\] \= final\_price

 entry\["pnl"\] \= (

(final\_price \- entry\["buy\_price"\]) / entry\["buy\_price"\] \* 100

 if final\_price is not None

 else None

)

 return results, buy\_entries

if \_\_name\_\_ \== "\_\_main\_\_":

 symbol \= input("Enter coin symbol to backtest: ").strip()

 results, buy\_entries \= run\_backtest\_single\_coin(prompt\_template, symbol)

 print("\\nAll recommendations:")

 for r in results:

 print(r)

 print("\\nBuy signals and PNL:")

 for b in buy\_entries:

 print(b)

 [view raw](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d/raw/f7b239c46a8f41a99e7ea135b7ae95df46f9c592/backtest.py)   [backtest.py](https://gist.github.com/CyberPunkMetalHead/1f2ff1b955b7a10ea202c903a069de5d#file-backtest-py) hosted with ❤ by [GitHub](https://github.com)

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
