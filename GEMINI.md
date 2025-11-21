# Diretrizes de Arquitetura e Desenvolvimento

*   **Arquitetura Modular / Hexagonal**: Separe domínio de infraestrutura (ports & adapters).
*   **Contratos Pydantic**: Todo módulo deve ter inputs/outputs explícitos definidos com `Pydantic`.
*   **Descoberta via API**: Não codifique valores fixos (limites da exchange, símbolos, etc.). Descubra tudo que for possível via API.
*   **Blocos Pequenos e Substituíveis**: Cada bloco deve ser focado, com interface estável e pronto para hot-swap.
*   **Toolchain Padrão**: Use `uv` + `hatchling`, `ruff`, `mypy`, `bandit`, `polars`, `vectorbt`.
*   **Priorize `ta-lib`**: Use `pandas_ta` como fallback e logue o evento.
*   **Dados Sensíveis**: Nunca no código. Use variáveis de ambiente. `.env` sempre no `.gitignore`.
*   **Logs Estruturados e Auditáveis**: Sempre logue `component`, `version`, `request_id`, e decisões importantes.

## Princípios de Design Obrigatórios

### 1. Arquitetura Hexagonal e Contratos de Dados
*   **Separação de Domínio**: Isole a lógica de negócio (`screening/`, `scoring/`) da infraestrutura (`adapters/binance`, `adapters/coingecko`).
*   **Padrão Ports & Adapters**:
    *   **Ports**: Interfaces ou classes abstratas que definem o que um módulo faz (ex: `ScoringPort`).
    *   **Adapters**: Implementações concretas (ex: `BinanceMarketDataAdapter`).
*   **Contratos Pydantic Obrigatórios**:
    *   **TODO MÓDULO** deve definir seus inputs e outputs usando modelos `Pydantic`. Isso é a base da nossa API interna e garante a integridade do fluxo de dados.
    *   Ex: `StrategySignalRequest` -> `StrategySignalResponse`.

### 2. API-First / Schema Discovery
*   Sempre que a exchange ou um serviço externo disponibilizar dados via API, você deve:
    *   Criar/adaptar um módulo de descoberta que chama a API.
    *   Persistir o resultado em artefatos versionados (`artifacts/exchange_schema/schema.json`).
*   **NUNCA** introduza constantes mágicas para `minNotional`, `minQty`, `stepSize`, etc.

### 3. Blocos Pequenos e Substituíveis (Hot Swap)
*   Cada bloco deve ter uma responsabilidade única e estar pronto para ter múltiplas versões (`v1`, `v2`).
*   Use um registry (`strategy_registry`, `scorer_registry`) para carregar implementações dinamicamente, permitindo hot-swap e shadow testing.

## Tecnologia e Toolchain
*   **Linguagem**: Python 3.11+.
*   **Gestão de projeto**: `pyproject.toml` com `uv` + `hatchling`.
*   **Dataframes**: Priorizar `Polars`. Usar `Pandas` apenas como fallback necessário.
*   **Backtest**: `vectorbt` (motor vetorizado com custos reais).
*   **Otimização**: `optuna` (com pruners).
*   **Indicadores**:
    *   **Prioridade 1**: `ta-lib` (performance).
    *   **Prioridade 2**: `pandas_ta` (fallback).
    *   **Regra**: Se `ta-lib` não estiver disponível, use `pandas_ta` e gere um log de nível `warning` informando o fallback.
*   **Qualidade**: `ruff`, `pylint`, `mypy`, `pyright`, `bandit`.

## Auto-Calibração, Otimização e Flywheel
*   **Backtest Vetorizado (`vectorbt`)**: Simule operações com custos reais.
*   **Otimização de Hiperparâmetros (`Optuna`)**: Otimize os parâmetros das estratégias usando Walk-Forward Optimization (WFO).
*   **Flywheel Effect**: Os resultados da otimização devem gerar novas versões de parâmetros ou estratégias, que são então validadas em *shadow mode* e promovidas, fechando o ciclo de melhoria contínua. Ao implementar o módulo de otimização, você deve:
    *   **Otimizar Parâmetros**: Ajustar os valores dos indicadores da estratégia.
    *   **Descobrir o Timeframe de Maior Retorno**: Testar a estratégia em múltiplos timeframes suportados para encontrar aquele com a melhor performance ajustada ao risco.
    *   **Atualizar o Registry**: Salvar os novos parâmetros e o timeframe ótimo no registry da estratégia para que o Módulo E possa usá-los.

## Logs, Auditoria e Self-Healing
*   **Logs Estruturados**: Gere logs em JSON com campos mínimos: `component`, `version`, `request_id`, `symbol`, `decision`, `reason`.
*   **Idempotência**: Garanta que re-executar um módulo não cause efeitos colaterais.
*   **Self-Healing**: Implemente backoff/retry para APIs e contribua para a detecção de anomalias (gaps de dados, etc.).

## Segurança e Segredos
*   Nunca inclua chaves de API, tokens ou senhas no repositório.
*   Leia segredos via `os.environ` ou um serviço de gerenciamento de segredos.
*   Garanta que `.env` esteja no `.gitignore`.

## Workflow Esperado para um Agent Code AI
1.  **Identifique o domínio**: "Nova estratégia", "Novo critério de scoring", etc.
2.  **Leia os artefatos relevantes**.
3.  **Defina o contrato**: Especifique os modelos `Pydantic` de input/output do novo bloco.
4.  **Implemente a lógica**: Crie a funcionalidade de forma coesa e com testes.
5.  **Integre com o registry**: Registre a nova versão do componente.
6.  **Documente no código**: Docstrings claras e comentários que expliquem o "porquê".