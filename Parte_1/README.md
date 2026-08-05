# README - Parte I 

Este documento descreve o trabalho realizado na Parte I, incluindo a preparação inicial da base de dados SQLite, a redução do volume de dados, a exportação para ficheiros CSV, a criação da staging area, a construção do  **DisGeNET cube** na conta **team_06**, o carregamento de dados a partir da conta **sbd24_114932** e dois exemplos de índices para melhoria de desempenho.

## Organização do trabalho

O trabalho foi dividido em quatro etapas principais:

1. Preparação inicial da base de dados **disgenet.2020** em SQLite.
2. Redução do volume de dados e exportação das tabelas para **ficheiros CSV**.
3. Importação dos CSV para a staging area em **sbd24_114932**.
4. Criação e carregamento do **DisGeNET cube** em **team_06**.

Esta sequência permitiu começar com a base original, gerar um subconjunto mais pequeno e controlado dos dados e só depois importá-lo para o ambiente SQL Server.

## Preparação inicial dos dados

Numa primeira fase, foi utilizada a base de dados original **disgenet.2020**, em SQLite, para preparar os dados antes da importação para SQL Server. Nesta fase, foram analisadas as tabelas de origem e identificadas as principais entidades e relações relevantes para o trabalho, nomeadamente diseaseAttributes, geneAttributes, variantAttributes, geneDiseaseNetwork, variantDiseaseNetwork, diseaseClass, disease2class e variantGene.

O volume dos dados foi reduzido para que as tabelas fact tivessem 30 000 registos. Para isso, foi preparado  o **script 01_reduce.SQL** em SQLite para selecionar subconjuntos das tabelas principais e eliminar registos não referenciados das dimensões, preservando apenas os elementos necessários para as associações sobreviventes.

Depois da redução, as tabelas resultantes foram exportadas **manualmente** para **ficheiros CSV**, **excluindo a variantGene**. Estes ficheiros CSV foram depois usados para alimentar a staging area no SQL Server.

## Staging area e target database

O processo foi dividido em duas áreas distintas no SQL Server:

- **Staging area** em **sbd_114932**, onde foram importados os ficheiros CSV.
- **Target database/cube** em **team_06**, onde foi criado o modelo final.

A staging area foi usada para armazenar os dados importados em estado bruto, enquanto o cube foi criado através do **script 02_create_disgenet_cube.sql**, com uma estrutura orientada à análise e com tipos de dados finais mais adequados.

## Estrutura do DisGeNET cube

O modelo final contém as seguintes tabelas:

- `DIM_Gene(geneID, name, description)`
- `DIM_Disease(diseaseID, name, typeID)`
- `DIM_DiseaseType(typeID, name)`
- `DIM_Variant(variantID, chromosome, coord, consequence)`
- `DIM_Source(sourceID, name)`
- `FACT_GDA(FactGDAKey, geneID, diseaseID, sourceID, year, score, nPmid)`
- `FACT_VDA(FactVDAKey, variantID, diseaseID, sourceID, year, score, nPmid)`

As dimensões armazenam os atributos descritivos principais, enquanto as facts guardam as associações gene–disease e variant–disease.

## Chaves primárias e estrangeiras

As chaves do modelo foram definidas da seguinte forma:

- `DIM_Gene.geneID` é chave primária e é referenciada por `FACT_GDA.geneID`.
- `DIM_Disease.diseaseID` é chave primária e é referenciada por `FACT_GDA.diseaseID` e `FACT_VDA.diseaseID`.
- `DIM_Source.sourceID` é chave primária e é referenciada por `FACT_GDA.sourceID` e `FACT_VDA.sourceID`.
- `DIM_DiseaseType.typeID` é chave primária e é referenciada por `DIM_Disease.typeID`.
- `FACT_GDA.FactGDAKey` é chave primária.
- `FACT_VDA.FactVDAKey` é chave primária.

## Permissões de acesso

Para permitir a leitura dos dados da staging pela conta `team_06`, foram concedidas permissões mínimas de leitura (`SELECT`) sobre as tabelas necessárias da base `sbd24_114932` através do **script 03_grant_permissions.sql**.

## Transformação e carregamento de dados

Os dados foram carregados da staging para o cube através do **script 04_load_disgenet_cube.sql** que faz a transformação dos valores importados em `NVARCHAR` para os tipos finais do modelo. Sempre que necessário, foram usadas conversões com `TRY_CAST` para reduzir o risco de falha durante o ETL.

 Os identificadores internos da staging, como `geneNID`, `diseaseNID` e `variantNID`, foram usados para estabelecer correspondência com os identificadores analíticos finais, como `geneId`, `diseaseId` e `variantId`, que são os usados no cube.

## Ordem de execução dos scripts

A execução dos scripts foi feita pela seguinte ordem:

1. Análise da base **disgenet.2020** em SQLite. **(Script 01)**
2. Redução das tabelas fact para um volume mais pequeno.  **(Script 01)**
3. Limpeza das dimensões para manter apenas registos referenciados.  **(Script 01)**
4. Exportação das tabelas reduzidas para ficheiros CSV. **(Manual)**
5. Importação dos CSV para a staging em **sbd24_114932**. **(Manual)**
6. Criação do schema **cube** e das tabelas do DisGeNET cube em **team_06**. **(Script 02)**
7. Atribuição de permissões de leitura à conta **team_06** sobre as tabelas staging. **(Script 03)**
8. Carregamento dos dados da staging para as dimensões e fact tables do cube. **(Script 04)**

## Relação Disease–Disease Class

O esquema de origem inclui uma relação muitos-para-muitos entre `Disease` e `Disease Class`. Conceptualmente, esta situação pode ser resolvida com uma **bridge table**, que liga uma doença a várias classes sem repetir atributos. O principal problema desta solução é o aumento da complexidade do ETL e das queries, porque passam a existir mais joins e mais regras de caregamento. Outra opção seria **não a incluir** no cube e mantê-la apenas como contexto conceptual, mas isso simplifica o modelo à custa de perder detalhe analítico e flexibilidade nas consultas.

## Exemplos de índices para melhoria de desempenho

Foram preparados dois exemplos simples para demonstrar que o uso de índices pode melhorar o desempenho de consultas analíticas sobre as fact tables.

### Exemplo 1 — Índice em FACT_GDA(diseaseID)

Query:

``` sql
SELECT TOP 10 geneID, diseaseID, sourceID, [year], score
FROM cube.FACT_GDA
ORDER BY diseaseID;
```

Inicialmente esta query representava um valor de custo estimado perto dos 2.30, como é possível verificar pela figura abaixo.

![alt text](<./Images/Captura de ecrã 2026-05-26 175939.png>)

Índice:

``` sql
CREATE INDEX IX_FACT_GDA_diseaseID
ON cube.FACT_GDA (diseaseID);
```

Após a criação do índice este valor diminuí-o para aproximadamente 0.04.

![alt text](<./Images/Captura de ecrã 2026-05-26 180011.png>)

### Exemplo 2 — Índice em FACT_VDA(sourceID, year)

Consulta:

``` sql
SELECT TOP 10 variantID, diseaseID, sourceID, [year], score
FROM cube.FACT_VDA
ORDER BY sourceID, [year];
```

Inicialmente esta query representava um valor de custo estimado perto dos 2.25, como é possível verificar pela figura abaixo.

![alt text](<./Images/Captura de ecrã 2026-05-26 180033.png>)

Índice:

``` sql
CREATE INDEX IX_FACT_VDA_sourceID_year
ON cube.FACT_VDA (sourceID, [year]);
```

Após a criação do índice este valor diminuí-o para aproximadamente 0.04.

![alt text](<./Images/Captura de ecrã 2026-05-26 180053.png>)

Assim é possível observar as melhorias na performance de execução de queries com a criação de índices.


