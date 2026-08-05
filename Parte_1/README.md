# README - Parte I 

This document describes the work performed for the initial preparation of the SQLite database, data volume reduction, export to CSV files, creation of the staging area, construction of the **DisGeNET cube** and data loading.

## Work Organization

The work was divided into four main stages:

1. Initial preparation of the **disgenet.2020** database in SQLite.
2. Data volume reduction and export of the tables to **ficheiros CSV**.
3. Import of the CSVs into the staging area.
4. Creation and loading of the **DisGeNET cube**.

This sequence allowed starting with the original database, generating a smaller and more controlled subset of data, and only then importing it into the SQL Server environment.

## Initial Data Preparation

In a first phase, the original database **disgenet.2020**, in SQLite, was used to prepare the data before importing it into SQL Server. During this phase, the source tables were analysed, and the main entities and relationships relevant to the work were identified, namely diseaseAttributes, geneAttributes, variantAttributes, geneDiseaseNetwork, variantDiseaseNetwork, diseaseClass, disease2class, and variantGene.

The data volume was reduced so that the fact tables had 30,000 records. For this purpose, the **script 01_reduce.SQL** was prepared in SQLite to select subsets of the main tables and delete unreferenced records from the dimensions, preserving only the elements necessary for the surviving associations.

After the reduction, the resulting tables were exported manually to **CSV files**, excluding variantGene. These CSV files were then used to feed the staging area in SQL Server.

## Staging Area and Target Database

The process was divided into two distinct areas in SQL Server:

- **Staging area** in **sbd_114932**, where the CSV files were imported.
- **Target database/cube** in **team_06**, where the final model was created.

The staging area was used to store the imported data in a raw state, while the cube was created using **script 02_create_disgenet_cube.sql**, with an analytics-oriented structure and more suitable final data types.

## DisGeNET Cube Structure

The final model contains the following tables:

- `DIM_Gene(geneID, name, description)`
- `DIM_Disease(diseaseID, name, typeID)`
- `DIM_DiseaseType(typeID, name)`
- `DIM_Variant(variantID, chromosome, coord, consequence)`
- `DIM_Source(sourceID, name)`
- `FACT_GDA(FactGDAKey, geneID, diseaseID, sourceID, year, score, nPmid)`
- `FACT_VDA(FactVDAKey, variantID, diseaseID, sourceID, year, score, nPmid)`

The dimensions store the main descriptive attributes, while the facts store the gene–disease and variant–disease associations.

## Primary and Foreign Keys

The keys of the model were defined as follows:

- `DIM_Gene.geneID` is the primary key and is referenced by `FACT_GDA.geneID`.
- `DIM_Disease.diseaseID` is the primary key and is referenced by `FACT_GDA.diseaseID` and `FACT_VDA.diseaseID`.
- `DIM_Source.sourceID` is the primary key and is referenced by `FACT_GDA.sourceID` and `FACT_VDA.sourceID`.
- `DIM_DiseaseType.typeID` is the primary key and is referenced by `DIM_Disease.typeID`.
- `FACT_GDA.FactGDAKey` is the primary key.
- `FACT_VDA.FactVDAKey` is the primary key.

## Grant Permissions

To allow the reading of staging data by the team_06 account, minimum read permissions (SELECT) were granted on the necessary tables of the sbd24_114932 database via **script 03_grant_permissions.sql**.

## Data Transformation and Loading

The data was loaded from the staging to the cube via **script 04_load_disgenet_cube.sql**, which transforms the imported `NVARCHAR` values into the model's final data types. Whenever necessary, conversions using `TRY_CAST` were applied to reduce the risk of failure during the ETL process.

The internal staging identifiers, such as `geneNID`, `diseaseNID` and `variantNID`, were used to establish a match with the final analytical identifiers, such as `geneId`, `diseaseId` and `variantId`, which are used in the cube.

## Script Execution Order

The execution of the scripts followed this order:

1. Analysis of the **disgenet.2020** database in SQLite. **(Script 01)**
2. Reduction of the fact tables to a smaller volume. **(Script 01)**
3. Cleaning of the dimensions to keep only referenced records.**(Script 01)**
4. Export of the reduced tables to CSV files.**(Manual)**
5. Import of the CSVs into the staging area in **sbd24_114932**. **(Manual)**
6. Creation of the **cube** schema and the DisGeNET cube tables in **team_06**. **(Script 02)**
7. Assignment of read permissions to the **team_06** account over the staging tables. **(Script 03)**
8. Data loading from the staging area into the dimensions and fact tables of the cube. **(Script 04)**
