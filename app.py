import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, timedelta

# ---------------------------------------------------------------------------
# Configuración de rutas
# ---------------------------------------------------------------------------
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

COMIDAS_FILE      = DATA_DIR / "comidas.xlsx"
RECETAS_FILE      = DATA_DIR / "recetas.xlsx"
INGREDIENTES_FILE = DATA_DIR / "ingredientes.xlsx"
PLANIFICACION_FILE= DATA_DIR / "planificacion.xlsx"

DIAS_ES   = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES  = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

def format_fecha(d: date) -> str:
    return f"{DIAS_ES[d.weekday()]} {d.day} de {MESES_ES[d.month - 1]}"

# ---------------------------------------------------------------------------
# Datos de ejemplo (se crean solo si no existen los ficheros)
# ---------------------------------------------------------------------------
def init_data():
    if not COMIDAS_FILE.exists():
        pd.DataFrame({
            "nombre": [
                "Paella de pollo", "Lentejas con chorizo", "Pasta boloñesa",
                "Tortilla de patatas", "Arroz al horno", "Pollo asado",
                "Ensalada mixta", "Gazpacho",
                "Crema de calabacín", "Huevos revueltos con champiñones",
                "Ensalada de atún", "Salmón a la plancha",
                "Croquetas caseras", "Verduras a la plancha con huevo",
            ],
            "tipo": [
                "comida", "comida", "comida", "comida", "comida", "comida",
                "comida", "comida",
                "cena", "cena", "cena", "cena", "cena", "cena",
            ],
        }).to_excel(COMIDAS_FILE, index=False)

    if not RECETAS_FILE.exists():
        pd.DataFrame({
            "comida": [
                "Paella de pollo",              "Paella de pollo",      "Paella de pollo",   "Paella de pollo",
                "Lentejas con chorizo",         "Lentejas con chorizo", "Lentejas con chorizo",
                "Pasta boloñesa",               "Pasta boloñesa",       "Pasta boloñesa",    "Pasta boloñesa",
                "Tortilla de patatas",          "Tortilla de patatas",
                "Salmón a la plancha",          "Salmón a la plancha",
                "Crema de calabacín",           "Crema de calabacín",   "Crema de calabacín",
                "Huevos revueltos con champiñones", "Huevos revueltos con champiñones",
                "Ensalada de atún",             "Ensalada de atún",     "Ensalada de atún",
            ],
            "ingrediente": [
                "Arroz",        "Pollo",        "Pimiento rojo",    "Tomate frito",
                "Lentejas",     "Chorizo",      "Cebolla",
                "Pasta",        "Carne picada", "Tomate frito",     "Queso parmesano",
                "Patata",       "Huevos",
                "Salmón",       "Limón",
                "Calabacín",    "Cebolla",      "Caldo de verduras",
                "Huevos",       "Champiñones",
                "Atún en lata", "Lechuga",      "Tomate",
            ],
            "cantidad": [
                100,  300,  1,    200,
                150,  100,  1,
                100,  200,  200,  50,
                2,    3,
                200,  1,
                2,    1,    300,
                3,    200,
                2,    0.5,  2,
            ],
            "unidad": [
                "g",    "g",    "ud",   "ml",
                "g",    "g",    "ud",
                "g",    "g",    "ml",   "g",
                "ud",   "ud",
                "g",    "ud",
                "ud",   "ud",   "ml",
                "ud",   "g",
                "lata", "ud",   "ud",
            ],
        }).to_excel(RECETAS_FILE, index=False)

    if not INGREDIENTES_FILE.exists():
        pd.DataFrame({
            "ingrediente": [
                "Arroz",        "Pollo",        "Pimiento rojo",    "Tomate frito",
                "Lentejas",     "Chorizo",      "Cebolla",
                "Pasta",        "Carne picada", "Queso parmesano",
                "Patata",       "Huevos",
                "Salmón",       "Limón",
                "Calabacín",    "Caldo de verduras",
                "Champiñones",  "Atún en lata", "Lechuga",          "Tomate",
            ],
            "supermercado": [
                "Mercadona",    "Mercadona",    "Consum",           "Mercadona",
                "Consum",       "Mercadona",    "Cualquiera",
                "Consum",       "Mercadona",    "Consum",
                "Cualquiera",   "Mercadona",
                "Mercadona",    "Cualquiera",
                "Cualquiera",   "Mercadona",
                "Consum",       "Mercadona",    "Consum",           "Cualquiera",
            ],
        }).to_excel(INGREDIENTES_FILE, index=False)

    if not PLANIFICACION_FILE.exists():
        pd.DataFrame(columns=["fecha", "tipo", "comida", "personas"]).to_excel(
            PLANIFICACION_FILE, index=False
        )

init_data()

# ---------------------------------------------------------------------------
# Carga de datos
# ---------------------------------------------------------------------------
@st.cache_data(ttl=10)
def load_comidas():
    return pd.read_excel(COMIDAS_FILE)

@st.cache_data(ttl=10)
def load_recetas():
    return pd.read_excel(RECETAS_FILE)

@st.cache_data(ttl=10)
def load_ingredientes():
    return pd.read_excel(INGREDIENTES_FILE)

def load_planificacion():
    df = pd.read_excel(PLANIFICACION_FILE)
    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
    return df

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Cesta App", page_icon="🛒", layout="wide")

st.sidebar.title("🛒 Cesta App")
st.sidebar.markdown("---")
page = st.sidebar.radio("Sección", [
    "🗓️ Planificación",
    "🛍️ Lista de la compra",
    "📖 Recetas",
    "🏪 Ingredientes",
])

# ===========================================================================
# PÁGINA: PLANIFICACIÓN
# ===========================================================================
if page == "🗓️ Planificación":
    st.title("🗓️ Planificación de comidas")

    comidas_df = load_comidas()
    plan_df    = load_planificacion()

    # Número de personas
    default_personas = 2
    if not plan_df.empty:
        default_personas = int(plan_df["personas"].iloc[0])
    personas = st.number_input("👥 Número de personas", min_value=1, max_value=20, value=default_personas)

    st.markdown("---")

    # Opciones por tipo
    opciones_comida = ["— sin planificar —"] + sorted(
        comidas_df[comidas_df["tipo"] == "comida"]["nombre"].tolist()
    )
    opciones_cena = ["— sin planificar —"] + sorted(
        comidas_df[comidas_df["tipo"] == "cena"]["nombre"].tolist()
    )

    # Lookup de lo que ya está guardado
    plan_lookup = {}
    for _, row in plan_df.iterrows():
        plan_lookup[(row["fecha"], row["tipo"])] = row["comida"]

    today = date.today()
    dias  = [today + timedelta(days=i) for i in range(10)]
    selections = {}

    for d in dias:
        st.markdown(f"**📅 {format_fecha(d)}**")
        c1, c2 = st.columns(2)
        with c1:
            prev = plan_lookup.get((d, "comida"), "— sin planificar —")
            idx  = opciones_comida.index(prev) if prev in opciones_comida else 0
            selections[(d, "comida")] = st.selectbox(
                "🍽️ Comida", opciones_comida, index=idx, key=f"c_{d}"
            )
        with c2:
            prev = plan_lookup.get((d, "cena"), "— sin planificar —")
            idx  = opciones_cena.index(prev) if prev in opciones_cena else 0
            selections[(d, "cena")] = st.selectbox(
                "🌙 Cena", opciones_cena, index=idx, key=f"ce_{d}"
            )
        st.markdown("---")

    st.markdown("---")
    if st.button("💾 Guardar planificación", type="primary"):
        rows = [
            {"fecha": d, "tipo": tipo, "comida": comida, "personas": int(personas)}
            for (d, tipo), comida in selections.items()
            if comida != "— sin planificar —"
        ]
        pd.DataFrame(rows).to_excel(PLANIFICACION_FILE, index=False)
        st.success("✅ Planificación guardada.")
        st.cache_data.clear()

# ===========================================================================
# PÁGINA: LISTA DE LA COMPRA
# ===========================================================================
elif page == "🛍️ Lista de la compra":
    st.title("🛍️ Lista de la compra")

    plan_df        = load_planificacion()
    recetas_df     = load_recetas()
    ingredientes_df= load_ingredientes()

    if plan_df.empty:
        st.warning("No hay planificación guardada. Ve primero a la sección **Planificación**.")
        st.stop()

    n_personas = int(plan_df["personas"].iloc[0])
    st.info(f"Planificación para **{n_personas} persona(s)**")

    # Resumen de la planificación
    with st.expander("Ver planificación completa"):
        plan_df["fecha"] = pd.to_datetime(plan_df["fecha"]).dt.date
        for d in sorted(plan_df["fecha"].unique()):
            filas   = plan_df[plan_df["fecha"] == d]
            comida  = filas[filas["tipo"] == "comida"]["comida"].values
            cena    = filas[filas["tipo"] == "cena"]["comida"].values
            comida_str = comida[0] if len(comida) else "—"
            cena_str   = cena[0]   if len(cena)   else "—"
            st.write(f"**{format_fecha(d)}** — 🍽️ {comida_str} &nbsp;|&nbsp; 🌙 {cena_str}")

    st.markdown("---")

    # Calcular lista de la compra
    shopping       = []
    sin_receta     = []
    sin_supermercado = []

    for _, row in plan_df.iterrows():
        plato    = row["comida"]
        personas = int(row["personas"])
        receta   = recetas_df[recetas_df["comida"] == plato]

        if receta.empty:
            if plato not in sin_receta:
                sin_receta.append(plato)
            continue

        for _, ing in receta.iterrows():
            ingrediente = ing["ingrediente"]
            cantidad    = ing["cantidad"] * personas
            unidad      = ing["unidad"]

            store_row   = ingredientes_df[ingredientes_df["ingrediente"] == ingrediente]
            if store_row.empty:
                if ingrediente not in sin_supermercado:
                    sin_supermercado.append(ingrediente)
                supermercado = "Sin asignar"
            else:
                supermercado = store_row.iloc[0]["supermercado"]

            shopping.append({
                "ingrediente": ingrediente,
                "cantidad":    cantidad,
                "unidad":      unidad,
                "supermercado":supermercado,
            })

    if sin_receta:
        st.warning(f"⚠️ Sin receta definida: {', '.join(sin_receta)}")
    if sin_supermercado:
        st.warning(f"⚠️ Sin supermercado asignado: {', '.join(sin_supermercado)}")

    if not shopping:
        st.info("No hay ingredientes que mostrar.")
        st.stop()

    shop_df = pd.DataFrame(shopping)
    agg = (
        shop_df
        .groupby(["supermercado", "ingrediente", "unidad"], as_index=False)["cantidad"]
        .sum()
        .sort_values(["supermercado", "ingrediente"])
    )

    ORDEN = ["Mercadona", "Consum", "Pescatería", "Carnicería", "Cualquiera", "Sin asignar"]
    ICONOS= {"Mercadona": "🟢", "Consum": "🔵", "Pescatería": "🐟", "Carnicería": "🥩", "Cualquiera": "⚪", "Sin asignar": "⚠️"}

    cols = st.columns(len([s for s in ORDEN if s in agg["supermercado"].values]))
    col_idx = 0
    for super_name in ORDEN:
        subset = agg[agg["supermercado"] == super_name]
        if subset.empty:
            continue
        with cols[col_idx]:
            st.subheader(f"{ICONOS[super_name]} {super_name}")
            for _, r in subset.iterrows():
                st.write(f"- {r['ingrediente']}: **{r['cantidad']:g} {r['unidad']}**")
        col_idx += 1

# ===========================================================================
# PÁGINA: RECETAS
# ===========================================================================
elif page == "📖 Recetas":
    st.title("📖 Recetas")

    comidas_df  = load_comidas()
    recetas_df  = load_recetas()

    tab_ver, tab_platos = st.tabs(["Ingredientes por plato", "Gestionar platos"])

    # --- Tab: ingredientes ---
    with tab_ver:
        todos_los_platos = sorted(comidas_df["nombre"].tolist())
        plato_sel = st.selectbox("Selecciona un plato", todos_los_platos)

        subset = recetas_df[recetas_df["comida"] == plato_sel].copy().reset_index(drop=True)

        if subset.empty:
            st.info("Este plato aún no tiene receta. Añade ingredientes abajo.")

        edited = st.data_editor(
            subset[["ingrediente", "cantidad", "unidad"]] if not subset.empty
            else pd.DataFrame(columns=["ingrediente", "cantidad", "unidad"]),
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "unidad": st.column_config.SelectboxColumn(
                    "Unidad", options=["g", "kg", "ml", "l", "ud", "lata", "cucharada"]
                )
            },
        )

        if st.button("💾 Guardar receta"):
            edited = edited.dropna(subset=["ingrediente"])
            edited["comida"] = plato_sel
            otros  = recetas_df[recetas_df["comida"] != plato_sel]
            nuevo  = pd.concat(
                [otros, edited[["comida", "ingrediente", "cantidad", "unidad"]]],
                ignore_index=True
            )
            nuevo.to_excel(RECETAS_FILE, index=False)
            st.success("Receta guardada.")
            st.cache_data.clear()

    # --- Tab: platos ---
    with tab_platos:
        st.markdown("Añade, edita o elimina platos del catálogo.")
        edited_comidas = st.data_editor(
            comidas_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "tipo": st.column_config.SelectboxColumn("Tipo", options=["comida", "cena"])
            },
        )
        if st.button("💾 Guardar platos"):
            edited_comidas = edited_comidas.dropna(subset=["nombre"])
            edited_comidas.to_excel(COMIDAS_FILE, index=False)
            st.success("Lista de platos actualizada.")
            st.cache_data.clear()

# ===========================================================================
# PÁGINA: INGREDIENTES
# ===========================================================================
elif page == "🏪 Ingredientes":
    st.title("🏪 Ingredientes y supermercados")

    ingredientes_df = load_ingredientes()

    st.markdown("Asigna cada ingrediente al supermercado donde lo compras habitualmente.")

    edited = st.data_editor(
        ingredientes_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "supermercado": st.column_config.SelectboxColumn(
                "Supermercado", options=["Mercadona", "Consum", "Pescatería", "Carnicería", "Cualquiera"]
            )
        },
    )

    if st.button("💾 Guardar", type="primary"):
        edited = edited.dropna(subset=["ingrediente"])
        edited.to_excel(INGREDIENTES_FILE, index=False)
        st.success("Lista de ingredientes actualizada.")
        st.cache_data.clear()
