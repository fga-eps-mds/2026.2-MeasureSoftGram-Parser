# MeasureSoftGram-Parser

## Badges

[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=fga-eps-mds_2026.1-MeasureSoftGram-Parser&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=fga-eps-mds_2026.1-MeasureSoftGram-Parser)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=fga-eps-mds_2026.1-MeasureSoftGram-Parser&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=fga-eps-mds_2026.1-MeasureSoftGram-Parser)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=fga-eps-mds_2026.1-MeasureSoftGram-Parser&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=fga-eps-mds_2026.1-MeasureSoftGram-Parser)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=fga-eps-mds_2026.1-MeasureSoftGram-Parser&metric=bugs)](https://sonarcloud.io/summary/new_code?id=fga-eps-mds_2026.1-MeasureSoftGram-Parser)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=fga-eps-mds_2026.1-MeasureSoftGram-Parser&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=fga-eps-mds_2026.1-MeasureSoftGram-Parser)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=fga-eps-mds_2026.1-MeasureSoftGram-Parser&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=fga-eps-mds_2026.1-MeasureSoftGram-Parser)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=fga-eps-mds_2026.1-MeasureSoftGram-Parser&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=fga-eps-mds_2026.1-MeasureSoftGram-Parser)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=fga-eps-mds_2026.1-MeasureSoftGram-Parser&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=fga-eps-mds_2026.1-MeasureSoftGram-Parser)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=fga-eps-mds_2026.1-MeasureSoftGram-Parser&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=fga-eps-mds_2026.1-MeasureSoftGram-Parser)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=fga-eps-mds_2026.1-MeasureSoftGram-Parser&metric=coverage)](https://sonarcloud.io/summary/new_code?id=fga-eps-mds_2026.1-MeasureSoftGram-Parser)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=fga-eps-mds_2026.1-MeasureSoftGram-Parser&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=fga-eps-mds_2026.1-MeasureSoftGram-Parser)


## Sobre o repositório

O principal objetivo do `MeasureSoftGram-Parser` é consumir e interpretar dados brutos (métricas e análises estáticas) provenientes de diferentes fontes e ferramentas externas de integração (como SonarQube, GitHub, Code Climate, entre outras). 

Suas responsabilidades incluem:
- **Coleta de Métricas:** Interagir com APIs de serviços de análise de código para extrair dados de qualidade (como *Code Smells*, *Bugs*, vulnerabilidades, cobertura de testes, etc.).
- **Padronização (Parsing):** Traduzir e normalizar esses dados heterogêneos para um formato padrão, garantindo que o serviço principal (Core) do MeasureSoftGram consiga processá-los e gerar as visualizações gráficas e relatórios finais.
- **Extensibilidade:** Facilitar a integração contínua de novas ferramentas analíticas ao projeto no futuro, mantendo a responsabilidade de extração desacoplada do resto do sistema.

A documentação completa, instruções de instalação e o guia oficial deste projeto estão centralizados no nosso repositório de documentação.

Acessse a documentação completa por aqui:
[Documentação Completa](https://fga-eps-mds.github.io/MeasureSoftGram-Docs/docs/intro/)


Para mais detalhes sobre o repositório Parser, acesse aqui:
[Documentação - Parser](https://fga-eps-mds.github.io/MeasureSoftGram-Docs/docs/componente-parser/)

## Licença

Este projeto está sob a licença AGPL-3.0.
