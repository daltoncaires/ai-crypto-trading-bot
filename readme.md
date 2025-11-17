# AI Crypto Trading Bot

[English](#en) | [Português (BR)](#pt-br)

---

<a name="en"></a>
## English

This is a minimal, modular AI-powered crypto trading bot for learning, experimentation, and rapid prototyping. It combines AI decision-making with real-time and historical crypto market data for automated trading strategies.

### Features
- Loads and manages coin, order, and portfolio data using simple JSON-based DALs (Data Access Layers).
- Fetches live and historical price data from CoinGecko.
- Uses OpenAI to generate buy/sell recommendations based on market context and configurable prompts.
- Simulates trading logic, including buy/sell handling, portfolio updates, and PnL tracking.
- Includes a backtesting module to evaluate AI-driven strategies on historical data.
- All configuration is handled via environment variables for easy tuning.
- **API-Driven Configuration**: Adapts to the available data from the CoinGecko API, ensuring resilience to changes and gracefully handling missing data points.

### API-Driven Configuration (Schema Discovery)
A core principle of this bot is to adapt to the data provided by the external API (CoinGecko). Instead of relying on hardcoded parameters, the bot discovers available information, such as the list of top coins, and adjusts its behavior accordingly.

This approach provides several advantages:
- **Resilience**: The bot is less likely to break if the API schema changes or if certain data points are temporarily unavailable.
- **Adaptability**: The bot automatically incorporates new coins as they enter the top market cap rankings.
- **Dynamic Rate Limiting**: While the CoinGecko Demo API does not provide rate limit headers, the bot uses a conservative delay between API calls to avoid `429 Too Many Requests` errors. This can be extended to a more dynamic strategy if using a Pro plan.

The decision-making engine is designed to be aware of and utilize the data schema as provided by the exchange/broker, making it more robust and adaptable to real-world conditions.

### Getting Started

#### Prerequisites
- Python 3.11+
- A CoinGecko Demo API Key
- An OpenAI API Key

#### Installation
1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/ai-crypto-trading-bot.git
    cd ai-crypto-trading-bot
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows, use `env\Scripts\activate`
    ```
3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

#### Configuration
1.  Create a `.env` file in the project root by copying the `.env.example` file.
2.  Add your CoinGecko and OpenAI API keys to the `.env` file:
    ```
    CG_API_KEY="YOUR_COINGECKO_DEMO_API_KEY"
    OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
    ```
3.  Configure the trading parameters in the `.env` file as needed.

### Usage

#### Running the Bot
To run the trading bot, execute the `main.py` script:
```bash
python main.py
```

#### Backtesting
To backtest a strategy on a single coin, run the `backtest.py` script and enter the coin symbol when prompted:
```bash
python backtest.py
```

### Risk Mitigation & Disclaimer
AI-powered trading involves significant risks. While this bot includes basic safety checks, it is not foolproof.
- **Always start with paper trading.**
- The AI can "hallucinate" or make incorrect recommendations.
- Market conditions can change rapidly.
- This bot is for educational purposes and should not be used for live trading without extensive testing and modification.

### Possible Improvements
- **Async Support**: Refactor to use `asyncio` for improved performance.
- **Postgres Database**: Replace JSON storage with a robust database.
- **Dockerization**: Add Docker support for easy deployment.
- **Advanced Logging**: Integrate a more advanced logging framework.
- **Unit & Integration Tests**: Add automated tests for reliability.
- **Web Dashboard**: Build a dashboard to visualize trades and performance.

### Credits & Original Source
This project is a fork and modification of the AI Crypto Trading Bot tutorial by [Cryptomaton on CoinGecko](https://www.coingecko.com/learn/build-ai-crypto-trading-bot).
The original source code can be found on [GitHub](https://github.com/CyberPunkMetalHead/ai-crypto-trading-bot).

---

<a name="pt-br"></a>
## Português (BR)

Este é um bot de negociação de criptomoedas minimalista e modular, alimentado por IA, para aprendizado, experimentação e prototipagem rápida. Ele combina a tomada de decisões de IA com dados de mercado de criptomoedas em tempo real e históricos para estratégias de negociação automatizadas.

### Funcionalidades
- Carrega e gerencia dados de moedas, ordens e portfólio usando DALs (Camadas de Acesso a Dados) simples baseadas em JSON.
- Busca dados de preços ao vivo e históricos do CoinGecko.
- Usa a OpenAI para gerar recomendações de compra/venda com base no contexto do mercado e em prompts configuráveis.
- Simula a lógica de negociação, incluindo o manuseio de compra/venda, atualizações de portfólio e acompanhamento de PnL (Lucros e Perdas).
- Inclui um módulo de backtesting para avaliar estratégias orientadas por IA em dados históricos.
- Toda a configuração é tratada por meio de variáveis de ambiente para fácil ajuste.
- **Configuração Orientada à API**: Adapta-se aos dados disponíveis da API do CoinGecko, garantindo resiliência a mudanças e lidando de forma elegante com pontos de dados ausentes.

### Configuração Orientada à API (Schema Discovery)
Um princípio central deste bot é se adaptar aos dados fornecidos pela API externa (CoinGecko). Em vez de depender de parâmetros fixos no código, o bot descobre as informações disponíveis, como a lista das principais moedas, e ajusta seu comportamento de acordo.

Esta abordagem oferece várias vantagens:
- **Resiliência**: O bot é menos propenso a quebrar se o schema da API mudar ou se certos pontos de dados estiverem temporariamente indisponíveis.
- **Adaptabilidade**: O bot incorpora automaticamente novas moedas à medida que elas entram no ranking de maior capitalização de mercado.
- **Limitação de Taxa Dinâmica**: Embora a API de demonstração do CoinGecko não forneça cabeçalhos de limite de taxa, o bot usa um atraso conservador entre as chamadas de API para evitar erros `429 Too Many Requests`. Isso pode ser estendido para uma estratégia mais dinâmica se for usado um plano Pro.

O motor de decisão é projetado para estar ciente e utilizar o schema de dados conforme fornecido pela exchange/broker, tornando-o mais robusto e adaptável às condições do mundo real.

### Começando

#### Pré-requisitos
- Python 3.11+
- Uma chave de API de demonstração do CoinGecko
- Uma chave de API da OpenAI

#### Instalação
1.  Clone o repositório:
    ```bash
    git clone https://github.com/your-username/ai-crypto-trading-bot.git
    cd ai-crypto-trading-bot
    ```
2.  Crie e ative um ambiente virtual:
    ```bash
    python -m venv env
    source env/bin/activate  # No Windows, use `env\Scripts\activate`
    ```
3.  Instale as dependências necessárias:
    ```bash
    pip install -r requirements.txt
    ```

#### Configuração
1.  Crie um arquivo `.env` na raiz do projeto copiando o arquivo `.env.example`.
2.  Adicione suas chaves de API do CoinGecko and OpenAI ao arquivo `.env`:
    ```
    CG_API_KEY="SUA_CHAVE_DE_API_DEMO_DO_COINGECKO"
    OPENAI_API_KEY="SUA_CHAVE_DE_API_DA_OPENAI"
    ```
3.  Configure os parâmetros de negociação no arquivo `.env` conforme necessário.

### Uso

#### Executando o Bot
Para executar o bot de negociação, execute o script `main.py`:
```bash
python main.py
```

#### Backtesting
Para testar uma estratégia em uma única moeda, execute o script `backtest.py` e insira o símbolo da moeda quando solicitado:
```bash
python backtest.py
```

### Mitigação de Riscos & Aviso Legal
A negociação com IA envolve riscos significativos. Embora este bot inclua verificações básicas de segurança, ele não é infalível.
- **Sempre comece com paper trading (negociação simulada).**
- A IA pode "alucinar" ou fazer recomendações incorretas.
- As condições de mercado podem mudar rapidamente.
- Este bot é para fins educacionais e não deve ser usado para negociações reais sem testes extensivos e modificações.

### Possíveis Melhorias
- **Suporte Assíncrono**: Refatorar para usar `asyncio` para melhor desempenho.
- **Banco de Dados Postgres**: Substituir o armazenamento em JSON por um banco de dados robusto.
- **Dockerização**: Adicionar suporte ao Docker para fácil implantação.
- **Logging Avançado**: Integrar um framework de logging mais avançado.
- **Testes Unitários e de Integração**: Adicionar testes automatizados para confiabilidade.
- **Painel Web**: Construir um painel para visualizar negociações e desempenho.

### Créditos & Fonte Original
Este projeto é um fork e uma modificação do tutorial AI Crypto Trading Bot por [Cryptomaton no CoinGecko](https://www.coingecko.com/learn/build-ai-crypto-trading-bot).
O código-fonte original pode ser encontrado no [GitHub](https://github.com/CyberPunkMetalHead/ai-crypto-trading-bot).
