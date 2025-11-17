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
- **Component Versioning**: Supports dynamic loading of different versions of core components (Evaluator, Strategy) via environment variables, enabling A/B testing and phased rollouts.
- **Shadow Mode**: Allows a new version of a component to run in parallel with the production version, processing the same inputs and logging its outputs without affecting live trading decisions. This is crucial for safely testing and validating new component versions in a production-like environment.

### Component Versioning & Shadow Mode
The bot supports dynamic loading of different component versions and a "shadow mode" for safe testing.

#### Component Versioning
You can specify which version of the `Evaluator` and `Strategy` components the bot should use by setting the following environment variables in your `.env` file:
- `EVALUATOR_VERSION`: (Default: `v1`) Set to `v1`, `v2`, or any custom version string. The bot will attempt to load `EvaluatorV<VERSION>` (e.g., `EvaluatorV2`). If the versioned class is not found, it falls back to the unversioned `Evaluator` class.
- `STRATEGY_VERSION`: (Default: `v1`) Similar to `EVALUATOR_VERSION`, set to `v1`, `v2`, etc. The bot will attempt to load `StrategyV<VERSION>` (e.g., `StrategyV2`).

To create a new version, simply create a new Python file (e.g., `domain/evaluator_v2.py`) and define your class as `EvaluatorV2` (or `StrategyV2`).

#### Shadow Mode
Shadow mode allows you to run an alternative version of your `Evaluator` and `Strategy` components in parallel with your live trading components. The shadow components receive the same inputs as the production components, execute their logic, and log their results, but their decisions do NOT affect live trades. This is invaluable for testing new features or optimizations in a production environment without risk.

To enable and configure shadow mode, set the following environment variables in your `.env` file:
- `SHADOW_MODE_ENABLED`: Set to `"True"` to enable shadow mode. (Default: `"False"`)
- `SHADOW_EVALUATOR_MODULE`: (Optional) The module path for the shadow Evaluator (e.g., `domain.evaluator_v2`). If not set, it defaults to the production `EVALUATOR_MODULE`.
- `SHADOW_EVALUATOR_CLASS`: (Optional) The class name for the shadow Evaluator (e.g., `EvaluatorV2`). If not set, it defaults to the production `EVALUATOR_CLASS`.
- `SHADOW_STRATEGY_MODULE`: (Optional) The module path for the shadow Strategy (e.g., `domain.strategy_v2`). If not set, it defaults to the production `STRATEGY_MODULE`.
- `SHADOW_STRATEGY_CLASS`: (Optional) The class name for the shadow Strategy (e.g., `StrategyV2`). If not set, it defaults to the production `STRATEGY_CLASS`.

When shadow mode is enabled, the bot will log the decisions and outcomes of both the production and shadow components, allowing you to compare their behavior.

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

#### Optimization
To run the Walk-Forward Optimizer and evaluate the strategy's performance realistically, run the `optimizer.py` script:
```bash
python optimizer.py
```
This will test the strategy on historical data, providing a more robust performance assessment than a simple backtest and laying the groundwork for hyperparameter tuning.

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
- **Versionamento de Componentes**: Suporta o carregamento dinâmico de diferentes versões dos componentes principais (Evaluator, Strategy) através de variáveis de ambiente, permitindo testes A/B e lançamentos faseados.
- **Modo Sombra (Shadow Mode)**: Permite que uma nova versão de um componente seja executada em paralelo com a versão de produção, processando as mesmas entradas e registrando suas saídas sem afetar as decisões de negociação ao vivo. Isso é crucial para testar e validar com segurança novas versões de componentes em um ambiente semelhante ao de produção.

### Versionamento de Componentes e Modo Sombra
O bot suporta o carregamento dinâmico de diferentes versões de componentes e um "modo sombra" para testes seguros.

#### Versionamento de Componentes
Você pode especificar qual versão dos componentes `Evaluator` e `Strategy` o bot deve usar definindo as seguintes variáveis de ambiente no seu arquivo `.env`:
- `EVALUATOR_VERSION`: (Padrão: `v1`) Defina como `v1`, `v2` ou qualquer string de versão personalizada. O bot tentará carregar `EvaluatorV<VERSAO>` (por exemplo, `EvaluatorV2`). Se a classe versionada não for encontrada, ele retornará à classe `Evaluator` sem versão.
- `STRATEGY_VERSION`: (Padrão: `v1`) Semelhante a `EVALUATOR_VERSION`, defina como `v1`, `v2`, etc. O bot tentará carregar `StrategyV<VERSAO>` (por exemplo, `StrategyV2`).

Para criar uma nova versão, basta criar um novo arquivo Python (por exemplo, `domain/evaluator_v2.py`) e definir sua classe como `EvaluatorV2` (ou `StrategyV2`).

#### Modo Sombra (Shadow Mode)
O modo sombra permite que você execute uma versão alternativa dos seus componentes `Evaluator` e `Strategy` em paralelo com seus componentes de negociação ao vivo. Os componentes sombra recebem as mesmas entradas que os componentes de produção, executam sua lógica e registram suas saídas, mas suas decisões NÃO afetam as negociações ao vivo. Isso é inestimável para testar novas funcionalidades ou otimizações em um ambiente de produção sem riscos.

Para habilitar e configurar o modo sombra, defina as seguintes variáveis de ambiente no seu arquivo `.env`:
- `SHADOW_MODE_ENABLED`: Defina como `"True"` para habilitar o modo sombra. (Padrão: `"False"`)
- `SHADOW_EVALUATOR_MODULE`: (Opcional) O caminho do módulo para o Evaluator sombra (por exemplo, `domain.evaluator_v2`). Se não for definido, o padrão é o `EVALUATOR_MODULE` de produção.
- `SHADOW_EVALUATOR_CLASS`: (Opcional) O nome da classe para o Evaluator sombra (por exemplo, `EvaluatorV2`). Se não for definido, o padrão é o `EVALUATOR_CLASS` de produção.
- `SHADOW_STRATEGY_MODULE`: (Opcional) O caminho do módulo para a Strategy sombra (por exemplo, `domain.strategy_v2`). Se não for definido, o padrão é o `STRATEGY_MODULE` de produção.
- `SHADOW_STRATEGY_CLASS`: (Opcional) O nome da classe para a Strategy sombra (por exemplo, `StrategyV2`). Se não for definido, o padrão é o `STRATEGY_CLASS` de produção.

Quando o modo sombra está habilitado, o bot registrará as decisões e os resultados dos componentes de produção e sombra, permitindo que você compare seus comportamentos.

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

#### Otimização
Para executar o Otimizador Walk-Forward e avaliar o desempenho da estratégia de forma realista, execute o script `optimizer.py`:
```bash
python optimizer.py
```
Isso testará a estratégia em dados históricos, fornecendo uma avaliação de desempenho mais robusta do que um simples backtest e preparando o terreno para o ajuste de hiperparâmetros.

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
