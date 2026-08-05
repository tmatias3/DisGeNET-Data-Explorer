-- 04_load_disgenet_cube.sql

-- DIM_DiseaseType
INSERT INTO cube.DIM_DiseaseType (name)
SELECT DISTINCT [type]
FROM sbd24_114932.stg.diseaseAttributes
WHERE [type] IS NOT NULL
  AND LTRIM(RTRIM([type])) <> '';
GO

-- DIM_Disease
INSERT INTO cube.DIM_Disease (diseaseID, name, typeID)
SELECT
    da.diseaseId,
    da.diseaseName,
    dt.typeID
FROM sbd24_114932.stg.diseaseAttributes da
LEFT JOIN cube.DIM_DiseaseType dt
    ON da.[type] = dt.name
WHERE da.diseaseId IS NOT NULL;
GO

-- DIM_Gene
INSERT INTO cube.DIM_Gene (geneID, name, description)
SELECT
    geneId,
    geneName,
    geneDescription
FROM sbd24_114932.stg.geneAttributes
WHERE geneId IS NOT NULL;
GO

-- DIM_Variant
INSERT INTO cube.DIM_Variant (variantID, chromosome, coord, consequence)
SELECT
    variantId,
    chromosome,
    TRY_CAST(coord AS BIGINT),
    most_severe_consequence
FROM sbd24_114932.stg.variantAttributes
WHERE variantId IS NOT NULL;
GO

-- DIM_Source
INSERT INTO cube.DIM_Source (name)
SELECT DISTINCT source
FROM (
    SELECT source FROM sbd24_114932.stg.geneDiseaseNetwork
    UNION
    SELECT source FROM sbd24_114932.stg.variantDiseaseNetwork
) s
WHERE source IS NOT NULL
  AND LTRIM(RTRIM(source)) <> '';
GO

-- FACT_GDA
INSERT INTO cube.FACT_GDA (geneID, diseaseID, sourceID, [year], score, nPmid)
SELECT
    ga.geneID,
    da.diseaseId,
    ds.sourceID,
    gdn.[year],
    ROUND(AVG(TRY_CAST(gdn.score AS FLOAT)), 3) AS score,
    COUNT(DISTINCT gdn.pmid) AS nPmid
FROM sbd24_114932.stg.geneDiseaseNetwork gdn
JOIN sbd24_114932.stg.geneAttributes ga
    ON ga.geneNID = gdn.geneNID
JOIN sbd24_114932.stg.diseaseAttributes da
    ON da.diseaseNID = gdn.diseaseNID
JOIN cube.DIM_Source ds
    ON ds.name = gdn.source
WHERE gdn.pmid IS NOT NULL
  AND TRY_CAST(gdn.score AS FLOAT) IS NOT NULL
GROUP BY
    ga.geneId,
    da.diseaseId,
    ds.sourceID,
    gdn.[year];
GO

-- FACT_VDA
INSERT INTO cube.FACT_VDA (variantID, diseaseID, sourceID, [year], score, nPmid)
SELECT
    va.variantId,
    da.diseaseId,
    ds.sourceID,
    vdn.[year],
    ROUND(AVG(TRY_CAST(vdn.score AS FLOAT)), 3) AS score,
    COUNT(DISTINCT vdn.pmid) AS nPmid
FROM sbd24_114932.stg.variantDiseaseNetwork vdn
JOIN sbd24_114932.stg.variantAttributes va
    ON va.variantNID = vdn.variantNID
JOIN sbd24_114932.stg.diseaseAttributes da
    ON da.diseaseNID = vdn.diseaseNID
JOIN cube.DIM_Source ds
    ON ds.name = vdn.source
WHERE vdn.pmid IS NOT NULL
  AND TRY_CAST(vdn.score AS FLOAT) IS NOT NULL
GROUP BY
    va.variantId,
    da.diseaseId,
    ds.sourceID,
    vdn.[year];
GO
