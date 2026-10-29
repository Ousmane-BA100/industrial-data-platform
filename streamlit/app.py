"""Application Streamlit de visualisation des marts exposes par FastAPI."""
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")
COLORS = ["#0E7490", "#0284C7", "#16A34A", "#D97706", "#DC2626", "#7C3AED"]
COLUMN_LABELS = {
    "product_id": "Identifiant produit",
    "name": "Nom",
    "family": "Famille de produits",
    "description": "Description",
    "unit_price": "Prix unitaire",
    "weight_kg": "Poids (kg)",
    "active": "Actif",
    "nb_components": "Nombre de composants",
    "total_components_qty": "Quantite totale de composants",
    "total_bom_cost": "Cout theorique de nomenclature",
    "estimated_margin": "Marge estimee",
    "component_id": "Identifiant composant",
    "component_description": "Designation du composant",
    "component_category": "Categorie de composant",
    "component_unit_price": "Prix unitaire du composant",
    "component_total_cost": "Cout total du composant",
    "quantity": "Quantite",
    "unit": "Unite",
    "machine_id": "Machine",
    "quantity_produced": "Quantite produite",
    "conformity_rate_pct": "Taux de conformite (%)",
    "production_events": "Nombre de lots produits",
    "inspections": "Nombre de controles",
    "passed_inspections": "Controles conformes",
    "failed_inspections": "Controles non conformes",
    "defect_code": "Type de defaut",
    "inspection_count": "Nombre de defauts",
    "defect_rate_pct": "Part des defauts (%)",
    "inventory_id": "Identifiant de stock",
    "material_id": "Identifiant materiau",
    "material_description": "Designation du materiau",
    "material_category": "Categorie de materiau",
    "warehouse": "Entrepot",
    "quantity_on_hand": "Quantite en stock",
    "quantity_reserved": "Quantite reservee",
    "quantity_available": "Quantite disponible",
    "reorder_level": "Seuil de reapprovisionnement",
    "last_movement": "Dernier mouvement",
    "is_below_reorder_level": "Sous le seuil de reapprovisionnement",
    "needs_replenishment": "Reapprovisionnement necessaire",
    "warehouse_count": "Nombre d'entrepots",
    "total_available_quantity": "Quantite totale disponible",
    "total_reorder_level": "Seuil total de reapprovisionnement",
    "warehouses_below_reorder_level": "Entrepots sous le seuil",
    "metric": "Indicateur",
    "amount": "Montant",
}

st.set_page_config(
    page_title="Industrial Data Platform",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=60, show_spinner=False)
def fetch(path, params=None):
    """Recupere une ressource JSON depuis FastAPI."""
    response = requests.get(f"{API_URL}{path}", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def frame(path, params=None):
    """Convertit une reponse liste en DataFrame."""
    return pd.DataFrame(fetch(path, params))


def display_frame(data):
    """Traduit les en-tetes sans modifier les noms utilises par l'API."""
    return data.rename(columns=COLUMN_LABELS)


def api_error(error):
    st.error(f"🚨 L'API est indisponible : {error}")
    st.info("Verifiez que le service `api` est demarre et que le pipeline Airflow a materialise les marts dbt.")


def page_header(icon, title, subtitle):
    st.title(f"{icon} {title}")
    st.caption(subtitle)


def configure_chart(figure):
    figure.update_layout(
        margin=dict(l=20, r=20, t=45, b=20),
        colorway=COLORS,
        legend_title_text="",
    )
    return figure


def overview_page():
    page_header("🏠", "Vue d'ensemble", "Indicateurs industriels issus des marts dbt")
    overview = fetch("/dashboard/overview")
    conformity = frame("/quality/conformity")
    replenishment = frame("/inventory/replenishment")

    metrics = st.columns(4)
    metrics[0].metric("Produits actifs", overview["active_products"])
    metrics[1].metric("Production totale", f"{overview['quantity_produced']:,}")
    metrics[2].metric("Conformite", f"{overview['conformity_rate_pct']:.1f}%")
    metrics[3].metric("A commander", overview["materials_to_replenish"])

    left, right = st.columns(2)
    with left:
        machine = conformity.groupby("machine_id", as_index=False).agg(
            conformity_rate_pct=("conformity_rate_pct", "mean")
        )
        chart = px.bar(
            machine,
            x="machine_id",
            y="conformity_rate_pct",
            title="Conformite moyenne par machine",
            range_y=[0, 100],
            text_auto=".1f",
            labels=COLUMN_LABELS,
        )
        st.plotly_chart(configure_chart(chart), use_container_width=True)
    with right:
        chart = px.bar(
            replenishment.head(10),
            x="material_id",
            y="total_available_quantity",
            color="needs_replenishment",
            title="Top 10 des alertes de reapprovisionnement",
            labels=COLUMN_LABELS,
        )
        st.plotly_chart(configure_chart(chart), use_container_width=True)


def quality_page():
    page_header("✅", "Qualite & production", "Conformite, inspections et defauts detectes")
    conformity = frame("/quality/conformity")
    defects = frame("/quality/top-defects")

    metrics = st.columns(3)
    metrics[0].metric("Inspections", f"{int(conformity['inspections'].sum()):,}")
    metrics[1].metric("Inspections conformes", f"{int(conformity['passed_inspections'].sum()):,}")
    metrics[2].metric("Defauts catalogues", len(defects))

    left, right = st.columns(2)
    with left:
        chart = px.scatter(
            conformity,
            x="quantity_produced",
            y="conformity_rate_pct",
            size="inspections",
            color="machine_id",
            hover_name="product_id",
            title="Production et taux de conformite",
            range_y=[0, 100],
            labels=COLUMN_LABELS,
        )
        st.plotly_chart(configure_chart(chart), use_container_width=True)
    with right:
        chart = px.bar(
            defects,
            x="inspection_count",
            y="defect_code",
            orientation="h",
            color="defect_rate_pct",
            title="Defauts les plus frequents",
            labels=COLUMN_LABELS,
        )
        st.plotly_chart(configure_chart(chart), use_container_width=True)

    st.subheader("📋 Detail par produit et machine")
    st.dataframe(
        display_frame(conformity.sort_values("conformity_rate_pct", ascending=False)),
        use_container_width=True,
        hide_index=True,
    )


def inventory_page():
    page_header("📦", "Stock & reapprovisionnement", "Stocks exploitables, seuils et alertes")
    inventory = frame("/inventory", {"limit": 500})
    replenishment = frame("/inventory/replenishment")

    warehouses = ["Tous"] + sorted(inventory["warehouse"].dropna().unique().tolist())
    selected_warehouse = st.selectbox("🏭 Entrepot", warehouses)
    if selected_warehouse != "Tous":
        inventory = inventory[inventory["warehouse"] == selected_warehouse]

    metrics = st.columns(3)
    metrics[0].metric("Lignes de stock", len(inventory))
    metrics[1].metric("Alertes a traiter", len(replenishment))
    metrics[2].metric("Entrepots", inventory["warehouse"].nunique())

    left, right = st.columns(2)
    with left:
        by_warehouse = inventory.groupby("warehouse", as_index=False).agg(
            quantity_available=("quantity_available", "sum"),
            reorder_level=("reorder_level", "sum"),
        )
        chart = go.Figure()
        chart.add_bar(name="Disponible", x=by_warehouse["warehouse"], y=by_warehouse["quantity_available"])
        chart.add_bar(name="Seuil", x=by_warehouse["warehouse"], y=by_warehouse["reorder_level"])
        chart.update_layout(title="Stock disponible vs seuil par entrepot", barmode="group")
        chart.update_xaxes(title_text=COLUMN_LABELS["warehouse"])
        chart.update_yaxes(title_text="Quantite")
        st.plotly_chart(configure_chart(chart), use_container_width=True)
    with right:
        category = inventory.groupby("material_category", as_index=False).agg(
            quantity_available=("quantity_available", "sum")
        )
        chart = px.pie(
            category,
            names="material_category",
            values="quantity_available",
            title="Repartition du stock disponible par categorie",
            labels=COLUMN_LABELS,
        )
        st.plotly_chart(configure_chart(chart), use_container_width=True)

    st.subheader("🚨 Materiaux a reapprovisionner")
    st.dataframe(display_frame(replenishment), use_container_width=True, hide_index=True)
    st.subheader("📋 Detail du stock par entrepot")
    st.dataframe(display_frame(inventory), use_container_width=True, hide_index=True)


def products_page():
    page_header("💰", "Produits & BOM", "Prix, cout theorique et composants")
    costs = frame("/products/costs")
    products = frame("/products", {"limit": 500})

    left, right = st.columns(2)
    with left:
        chart = px.scatter(
            costs,
            x="total_bom_cost",
            y="unit_price",
            color="family",
            size="nb_components",
            hover_name="product_id",
            title="Prix produit vs cout theorique de BOM",
            labels=COLUMN_LABELS,
        )
        st.plotly_chart(configure_chart(chart), use_container_width=True)
    with right:
        family_costs = costs.groupby("family", as_index=False).agg(
            total_bom_cost=("total_bom_cost", "mean"),
            unit_price=("unit_price", "mean"),
        )
        chart = px.bar(
            family_costs.melt(id_vars="family", var_name="metric", value_name="amount"),
            x="family",
            y="amount",
            color="metric",
            barmode="group",
            title="Prix et cout moyen par famille",
            labels=COLUMN_LABELS,
        )
        st.plotly_chart(configure_chart(chart), use_container_width=True)

    selected_product = st.selectbox("🔎 Produit a analyser", products["product_id"].tolist())
    product = fetch(f"/products/{selected_product}")
    components = pd.DataFrame(fetch(f"/products/{selected_product}/components")["components"])

    metrics = st.columns(3)
    metrics[0].metric("Prix unitaire", f"{product.get('unit_price', 0):,.2f}")
    metrics[1].metric("Cout de BOM", f"{product.get('total_bom_cost', 0):,.2f}")
    metrics[2].metric("Composants", product.get("nb_components", 0))

    left, right = st.columns([3, 2])
    with left:
        chart = px.bar(
            components,
            x="component_id",
            y="component_total_cost",
            color="component_category",
            title="Cout de la BOM par composant",
            labels=COLUMN_LABELS,
        )
        st.plotly_chart(configure_chart(chart), use_container_width=True)
    with right:
        st.subheader("📋 Composants")
        st.dataframe(display_frame(components), use_container_width=True, hide_index=True)


def guide_page():
    page_header("📖", "Guide d'utilisation", "Comment utiliser le dashboard et la plateforme")
    st.markdown("""
### 🚀 Demarrage

1. Lancez la plateforme avec `docker-compose up -d --build`.
2. Dans Airflow, declenchez `industrial_data_pipeline`.
3. Ouvrez ce dashboard sur `http://localhost:8501`.

### 🧭 Navigation

- **🏠 Vue d'ensemble** : les indicateurs de pilotage et les principales alertes.
- **✅ Qualite** : la conformite par machine, les inspections et les defauts.
- **📦 Stock** : le disponible, les seuils et les besoins de reapprovisionnement.
- **💰 Produits & BOM** : les couts de composants et la comparaison prix/cout.

### 🔄 Rafraichissement

Le dashboard conserve les reponses API pendant une minute. Utilisez le bouton **Actualiser les donnees** dans la barre laterale apres une nouvelle execution Airflow.

### 🛡️ Gouvernance des donnees

Cette application est en lecture seule. Les donnees sont mises a jour par les sources CSV, Airflow et dbt. Streamlit interroge FastAPI, qui expose uniquement les marts controles de `public_marts`.
""")
    st.graphviz_chart("""
    digraph pipeline {
      rankdir=LR;
      node [shape=box style=rounded];
      Sources -> Airflow -> PostgreSQL -> dbt -> FastAPI -> Streamlit;
    }
    """)


with st.sidebar:
    st.title("🏭 IDP")
    st.caption("Industrial Data Platform")
    page = st.radio(
        "Navigation",
        ["🏠 Vue d'ensemble", "✅ Qualite", "📦 Stock", "💰 Produits & BOM", "📖 Guide"],
        label_visibility="collapsed",
    )
    st.divider()
    if st.button("🔄 Actualiser les donnees", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.caption("Source : FastAPI / marts dbt")

try:
    if page == "🏠 Vue d'ensemble":
        overview_page()
    elif page == "✅ Qualite":
        quality_page()
    elif page == "📦 Stock":
        inventory_page()
    elif page == "💰 Produits & BOM":
        products_page()
    else:
        guide_page()
except requests.RequestException as error:
    api_error(error)
