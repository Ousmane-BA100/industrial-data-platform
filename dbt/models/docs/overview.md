{% docs __overview__ %}

![Industrial Data Platform — logo](assets/industrial-data-platform-logo.svg)

# Industrial Data Platform

Plateforme de donnees industrielles synthetiques reliant les referentiels SAP/ERP et PLM aux evenements de production et aux controles qualite.

## Parcours des donnees

```text
SAP / ERP + PLM
      ↓
  Tables RAW
      ↓
   Staging
      ↓
 Intermediate
      ↓
     Marts
      ↓
FastAPI → Streamlit
```

Les modeles `staging` reprennent les sources et signalent les anomalies. Les modeles `intermediate` relient les entites industrielles. Les `marts` exposent des dimensions, des faits et des KPI destines a l'analyse et aux applications.

## Domaines documentes

| Domaine | Modeles et indicateurs |
| --- | --- |
| Produits et nomenclatures | Produits finis, composants et cout theorique de BOM |
| Approvisionnement | Fournisseurs, matieres, commandes et delais |
| Stocks | Quantites disponibles et alertes de reapprovisionnement |
| Production | Volumes fabriques par produit et machine |
| Qualite | Inspections, defauts et taux de conformite |

## Qualite des donnees

Les stocks negatifs generes intentionnellement restent visibles dans `stg_inventory` pour illustrer le controle de qualite, puis sont exclus du mart de stock exploitable. Les tests dbt verifient egalement les references entre systemes, les quantites positives, la chronologie des inspections et la coherence des statuts qualite.

Les expositions `industrial_fastapi` et `industrial_streamlit_dashboard` representent les consommateurs aval dans le graphe de lineage.

{% enddocs %}