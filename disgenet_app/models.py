"""
Modelos para o DisGeNET cube.
Gerados a partir do esquema SQL Server existente na team_06 (schema: cube).
Usa managed=False para que o Django nunca tente criar/alterar tabelas.

db_table usa o formato: cube].[TABLE_NAME
O Django coloca-o diretamente em parêntesis retos, produzindo: [cube].[TABLE_NAME]
que é a síntese de esquema qualificado correta no SQL Server.
"""

from django.db import models


class DimDiseaseType(models.Model):
    typeID = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[cube].[DIM_DiseaseType]'
        ordering = ['name']

    def __str__(self):
        return self.name or self.typeID


class DimDisease(models.Model):
    diseaseID = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=500, blank=True, null=True)
    typeID = models.ForeignKey(
        DimDiseaseType,
        on_delete=models.DO_NOTHING,
        db_column='typeID',
        blank=True,
        null=True,
        related_name='diseases',
    )

    class Meta:
        managed = False
        db_table = '[cube].[DIM_Disease]'
        ordering = ['name']

    def __str__(self):
        return self.name or self.diseaseID


class DimGene(models.Model):
    geneID = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[cube].[DIM_Gene]'
        ordering = ['name']

    def __str__(self):
        return self.name or str(self.geneID)


class DimSource(models.Model):
    sourceID = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[cube].[DIM_Source]'

    def __str__(self):
        return self.name or self.sourceID


class DimVariant(models.Model):
    variantID = models.CharField(primary_key=True, max_length=100)
    chromosome = models.CharField(max_length=10, blank=True, null=True)
    coord = models.BigIntegerField(blank=True, null=True)
    consequence = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[cube].[DIM_Variant]'

    def __str__(self):
        return self.variantID


class FactGda(models.Model):
    FactGDAKey = models.BigIntegerField(primary_key=True)
    geneID = models.ForeignKey(DimGene, on_delete=models.DO_NOTHING, db_column='geneID')
    diseaseID = models.ForeignKey(DimDisease, on_delete=models.DO_NOTHING, db_column='diseaseID')
    sourceID = models.ForeignKey(DimSource, on_delete=models.DO_NOTHING, db_column='sourceID')
    year = models.IntegerField(blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    nPmid = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[cube].[FACT_GDA]'

    def __str__(self):
        return f"GDA({self.geneID_id} × {self.diseaseID_id})"


class FactVda(models.Model):
    FactVDAKey = models.BigIntegerField(primary_key=True)
    variantID = models.ForeignKey(DimVariant, on_delete=models.DO_NOTHING, db_column='variantID')
    diseaseID = models.ForeignKey(DimDisease, on_delete=models.DO_NOTHING, db_column='diseaseID')
    sourceID = models.ForeignKey(DimSource, on_delete=models.DO_NOTHING, db_column='sourceID')
    year = models.IntegerField(blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    nPmid = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = '[cube].[FACT_VDA]'

    def __str__(self):
        return f"VDA({self.variantID_id} × {self.diseaseID_id})"