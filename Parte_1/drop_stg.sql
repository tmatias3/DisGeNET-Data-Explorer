IF OBJECT_ID('stg.variantGene', 'U') IS NOT NULL DROP TABLE stg.variantGene;
IF OBJECT_ID('stg.variantDiseaseNetwork', 'U') IS NOT NULL DROP TABLE stg.variantDiseaseNetwork;
IF OBJECT_ID('stg.variantAttributes', 'U') IS NOT NULL DROP TABLE stg.variantAttributes;
IF OBJECT_ID('stg.geneDiseaseNetwork', 'U') IS NOT NULL DROP TABLE stg.geneDiseaseNetwork;
IF OBJECT_ID('stg.geneAttributes', 'U') IS NOT NULL DROP TABLE stg.geneAttributes;
IF OBJECT_ID('stg.disease2class', 'U') IS NOT NULL DROP TABLE stg.disease2class;
IF OBJECT_ID('stg.diseaseClass', 'U') IS NOT NULL DROP TABLE stg.diseaseClass;
IF OBJECT_ID('stg.diseaseAttributes', 'U') IS NOT NULL DROP TABLE stg.diseaseAttributes;
DROP SCHEMA IF EXISTS stg;