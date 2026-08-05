-- 01_reduce.sql

PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS keep_gdn;
CREATE TEMP TABLE keep_gdn AS
SELECT NID
FROM geneDiseaseNetwork
ORDER BY RANDOM()
LIMIT 30000;

DELETE FROM geneDiseaseNetwork
WHERE NID NOT IN (SELECT NID FROM keep_gdn);

DROP TABLE IF EXISTS keep_vdn;
CREATE TEMP TABLE keep_vdn AS
SELECT NID
FROM variantDiseaseNetwork
ORDER BY RANDOM()
LIMIT 30000;

DELETE FROM variantDiseaseNetwork
WHERE NID NOT IN (SELECT NID FROM keep_vdn);

DELETE FROM diseaseAttributes
WHERE diseaseNID NOT IN (
    SELECT diseaseNID FROM geneDiseaseNetwork
    UNION
    SELECT diseaseNID FROM variantDiseaseNetwork
);

DELETE FROM geneAttributes
WHERE geneNID NOT IN (
    SELECT geneNID FROM geneDiseaseNetwork
);

DELETE FROM variantAttributes
WHERE variantNID NOT IN (
    SELECT variantNID FROM variantDiseaseNetwork
);

DELETE FROM disease2class
WHERE diseaseNID NOT IN (
    SELECT diseaseNID FROM diseaseAttributes
);

DELETE FROM diseaseClass
WHERE diseaseClassNID NOT IN (
    SELECT diseaseClassNID FROM disease2class
);

DELETE FROM variantGene
WHERE variantNID NOT IN (
    SELECT variantNID FROM variantAttributes
)
OR geneNID NOT IN (
    SELECT geneNID FROM geneAttributes
);

COMMIT;
PRAGMA foreign_keys = ON;

SELECT 'geneDiseaseNetwork' AS table_name, COUNT(*) AS total_rows FROM geneDiseaseNetwork
UNION ALL
SELECT 'variantDiseaseNetwork', COUNT(*) FROM variantDiseaseNetwork
UNION ALL
SELECT 'diseaseAttributes', COUNT(*) FROM diseaseAttributes
UNION ALL
SELECT 'geneAttributes', COUNT(*) FROM geneAttributes
UNION ALL
SELECT 'variantAttributes', COUNT(*) FROM variantAttributes
UNION ALL
SELECT 'disease2class', COUNT(*) FROM disease2class
UNION ALL
SELECT 'diseaseClass', COUNT(*) FROM diseaseClass
UNION ALL
SELECT 'variantGene', COUNT(*) FROM variantGene;


VACUUM;