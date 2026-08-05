-- 02_create_disgenet_cube.sql

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'cube')
    EXEC('CREATE SCHEMA cube');
GO

DROP TABLE IF EXISTS cube.FACT_VDA;
DROP TABLE IF EXISTS cube.FACT_GDA;
DROP TABLE IF EXISTS cube.DIM_Source;
DROP TABLE IF EXISTS cube.DIM_Variant;
DROP TABLE IF EXISTS cube.DIM_Disease;
DROP TABLE IF EXISTS cube.DIM_DiseaseType;
DROP TABLE IF EXISTS cube.DIM_Gene;
GO

-- DIM_Gene
CREATE TABLE cube.DIM_Gene (
    geneID       INT PRIMARY KEY,
    name         NVARCHAR(200) NULL,
    description  NVARCHAR(MAX) NULL
);
GO

-- DIM_DiseaseType
CREATE TABLE cube.DIM_DiseaseType (
    typeID       INT IDENTITY(1,1) PRIMARY KEY,
    name         NVARCHAR(100) NOT NULL UNIQUE
);
GO

-- DIM_Disease
CREATE TABLE cube.DIM_Disease (
    diseaseID    NVARCHAR(100) PRIMARY KEY,
    name         NVARCHAR(400) NULL,
    typeID       INT NULL,
    CONSTRAINT FK_DIM_Disease_DiseaseType
        FOREIGN KEY (typeID) REFERENCES cube.DIM_DiseaseType(typeID)
);
GO

-- DIM_Variant
CREATE TABLE cube.DIM_Variant (
    variantID     NVARCHAR(100) PRIMARY KEY,
    chromosome    NVARCHAR(50) NULL,
    coord         BIGINT NULL,
    consequence   NVARCHAR(400) NULL
);
GO

-- DIM_Source
CREATE TABLE cube.DIM_Source (
    sourceID      INT IDENTITY(1,1) PRIMARY KEY,
    name          NVARCHAR(200) NOT NULL UNIQUE
);
GO

-- FACT_GDA
CREATE TABLE cube.FACT_GDA (
    FactGDAKey    INT IDENTITY(1,1) PRIMARY KEY,
    geneID        INT NOT NULL,
    diseaseID     NVARCHAR(100) NOT NULL,
    sourceID      INT NOT NULL,
    [year]        SMALLINT NULL,
    score         FLOAT NULL,
    nPmid         INT NULL,
    CONSTRAINT FK_FACT_GDA_Gene
        FOREIGN KEY (geneID) REFERENCES cube.DIM_Gene(geneID),
    CONSTRAINT FK_FACT_GDA_Disease
        FOREIGN KEY (diseaseID) REFERENCES cube.DIM_Disease(diseaseID),
    CONSTRAINT FK_FACT_GDA_Source
        FOREIGN KEY (sourceID) REFERENCES cube.DIM_Source(sourceID),
    CONSTRAINT UNIQUE_GDA 
        UNIQUE (geneID, diseaseID, sourceID, [year])
);
GO

-- FACT_VDA
CREATE TABLE cube.FACT_VDA (
    FactVDAKey    INT IDENTITY(1,1) PRIMARY KEY,
    variantID     NVARCHAR(100) NOT NULL,
    diseaseID     NVARCHAR(100) NOT NULL,
    sourceID      INT NOT NULL,
    [year]        SMALLINT NULL,
    score         FLOAT NULL,
    nPmid         INT NULL,
    CONSTRAINT FK_FACT_VDA_Variant
        FOREIGN KEY (variantID) REFERENCES cube.DIM_Variant(variantID),
    CONSTRAINT FK_FACT_VDA_Disease
        FOREIGN KEY (diseaseID) REFERENCES cube.DIM_Disease(diseaseID),
    CONSTRAINT FK_FACT_VDA_Source
        FOREIGN KEY (sourceID) REFERENCES cube.DIM_Source(sourceID),
    CONSTRAINT UNIQUE_VDA 
        UNIQUE (variantID, diseaseID, sourceID, [year])
);
GO
