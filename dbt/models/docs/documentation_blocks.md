{% docs product_bom_cost_overview %}

### Cout theorique de nomenclature

Ce modele agrege chaque nomenclature produit. Le cout correspond a la somme des quantites de composants multipliees par leur prix d'achat unitaire connu.

> Ce montant est un cout materiel estime pour une unite du produit. Il n'inclut ni main-d'oeuvre, ni cout de production, ni frais indirects.

{% enddocs %}

{% docs inventory_anomaly_policy %}

### Traitement des stocks negatifs

Les positions avec une quantite disponible negative sont des anomalies synthetiques intentionnelles. Elles sont conservees dans la couche staging afin que les tests Data Quality puissent les detecter, mais ne sont pas incluses dans le mart de stock utilise par les analyses et l'API.

{% enddocs %}

{% docs quality_conformity_rate %}

### Taux de conformite

Pourcentage des inspections dont le statut est `PASSED`, calcule par produit et machine parmi les inspections disponibles. Les productions sans inspection contribuent aux volumes de production, mais pas au denominateur du taux.

{% enddocs %}