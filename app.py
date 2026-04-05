import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import date, timedelta

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
DIAS_ES  = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

def format_fecha(d: date) -> str:
    return f"{DIAS_ES[d.weekday()]} {d.day} de {MESES_ES[d.month - 1]}"

# ---------------------------------------------------------------------------
# Conexión a Supabase
# ---------------------------------------------------------------------------
@st.cache_resource
def get_client():
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["key"],
    )

# ---------------------------------------------------------------------------
# Lectura / escritura de tablas
# ---------------------------------------------------------------------------
@st.cache_data(ttl=15)
def load_table(name: str) -> pd.DataFrame:
    sb = get_client()
    response = sb.table(name).select("*").execute()
    return pd.DataFrame(response.data)

def save_table(name: str, df: pd.DataFrame):
    sb = get_client()
    sb.table(name).delete().gte("id", 0).execute()
    if not df.empty:
        records = df.drop(columns=["id"], errors="ignore").to_dict("records")
        sb.table(name).insert(records).execute()

def load_comidas() -> pd.DataFrame:
    df = load_table("comidas")
    for col in ["comida", "cena"]:
        if col in df.columns:
            df[col] = df[col].astype(bool)
    return df

def load_planificacion() -> pd.DataFrame:
    df = load_table("planificacion")
    if not df.empty and "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce").dt.date
    return df

# ---------------------------------------------------------------------------
# Insertar datos de ejemplo si las tablas están vacías
# ---------------------------------------------------------------------------
def init_data():
    sb = get_client()

    if not sb.table("comidas").select("id").limit(1).execute().data:
        sb.table("comidas").insert([
            {"nombre": "Paella de pollo",                  "comida": True,  "cena": False},
            {"nombre": "Lentejas con chorizo",             "comida": True,  "cena": False},
            {"nombre": "Pasta boloñesa",                   "comida": True,  "cena": True},
            {"nombre": "Tortilla de patatas",              "comida": True,  "cena": True},
            {"nombre": "Arroz al horno",                   "comida": True,  "cena": False},
            {"nombre": "Pollo asado",                      "comida": True,  "cena": True},
            {"nombre": "Ensalada mixta",                   "comida": True,  "cena": True},
            {"nombre": "Gazpacho",                         "comida": True,  "cena": True},
            {"nombre": "Crema de calabacín",               "comida": False, "cena": True},
            {"nombre": "Huevos revueltos con champiñones", "comida": False, "cena": True},
            {"nombre": "Ensalada de atún",                 "comida": True,  "cena": True},
            {"nombre": "Salmón a la plancha",              "comida": False, "cena": True},
            {"nombre": "Croquetas caseras",                "comida": False, "cena": True},
            {"nombre": "Verduras a la plancha con huevo",  "comida": False, "cena": True},
        ]).execute()

    if not sb.table("recetas").select("id").limit(1).execute().data:
        sb.table("recetas").insert([
            {"comida": "Paella de pollo",              "ingrediente": "Arroz",         "cantidad": 100, "unidad": "g"},
            {"comida": "Paella de pollo",              "ingrediente": "Pollo",         "cantidad": 300, "unidad": "g"},
            {"comida": "Paella de pollo",              "ingrediente": "Pimiento rojo", "cantidad": 1,   "unidad": "ud"},
            {"comida": "Paella de pollo",              "ingrediente": "Tomate frito",  "cantidad": 200, "unidad": "ml"},
            {"comida": "Lentejas con chorizo",         "ingrediente": "Lentejas",      "cantidad": 150, "unidad": "g"},
            {"comida": "Lentejas con chorizo",         "ingrediente": "Chorizo",       "cantidad": 100, "unidad": "g"},
            {"comida": "Lentejas con chorizo",         "ingrediente": "Cebolla",       "cantidad": 1,   "unidad": "ud"},
            {"comida": "Pasta boloñesa",               "ingrediente": "Pasta",         "cantidad": 100, "unidad": "g"},
            {"comida": "Pasta boloñesa",               "ingrediente": "Carne picada",  "cantidad": 200, "unidad": "g"},
            {"comida": "Pasta boloñesa",               "ingrediente": "Tomate frito",  "cantidad": 200, "unidad": "ml"},
            {"comida": "Pasta boloñesa",               "ingrediente": "Queso parmesano","cantidad": 50, "unidad": "g"},
            {"comida": "Tortilla de patatas",          "ingrediente": "Patata",        "cantidad": 2,   "unidad": "ud"},
            {"comida": "Tortilla de patatas",          "ingrediente": "Huevos",        "cantidad": 3,   "unidad": "ud"},
            {"comida": "Salmón a la plancha",          "ingrediente": "Salmón",        "cantidad": 200, "unidad": "g"},
            {"comida": "Salmón a la plancha",          "ingrediente": "Limón",         "cantidad": 1,   "unidad": "ud"},
            {"comida": "Crema de calabacín",           "ingrediente": "Calabacín",     "cantidad": 2,   "unidad": "ud"},
            {"comida": "Crema de calabacín",           "ingrediente": "Cebolla",       "cantidad": 1,   "unidad": "ud"},
            {"comida": "Crema de calabacín",           "ingrediente": "Caldo de verduras","cantidad": 300,"unidad": "ml"},
            {"comida": "Huevos revueltos con champiñones","ingrediente": "Huevos",     "cantidad": 3,   "unidad": "ud"},
            {"comida": "Huevos revueltos con champiñones","ingrediente": "Champiñones","cantidad": 200, "unidad": "g"},
            {"comida": "Ensalada de atún",             "ingrediente": "Atún en lata",  "cantidad": 2,   "unidad": "lata"},
            {"comida": "Ensalada de atún",             "ingrediente": "Lechuga",       "cantidad": 1,   "unidad": "ud"},
            {"comida": "Ensalada de atún",             "ingrediente": "Tomate",        "cantidad": 2,   "unidad": "ud"},
        ]).execute()

    if not sb.table("ingredientes").select("id").limit(1).execute().data:
        sb.table("ingredientes").insert([
            {"ingrediente": "Arroz",            "supermercado": "Mercadona"},
            {"ingrediente": "Pollo",            "supermercado": "Mercadona"},
            {"ingrediente": "Pimiento rojo",    "supermercado": "Consum"},
            {"ingrediente": "Tomate frito",     "supermercado": "Mercadona"},
            {"ingrediente": "Lentejas",         "supermercado": "Consum"},
            {"ingrediente": "Chorizo",          "supermercado": "Mercadona"},
            {"ingrediente": "Cebolla",          "supermercado": "Cualquiera"},
            {"ingrediente": "Pasta",            "supermercado": "Consum"},
            {"ingrediente": "Carne picada",     "supermercado": "Mercadona"},
            {"ingrediente": "Queso parmesano",  "supermercado": "Consum"},
            {"ingrediente": "Patata",           "supermercado": "Cualquiera"},
            {"ingrediente": "Huevos",           "supermercado": "Mercadona"},
            {"ingrediente": "Salmón",           "supermercado": "Mercadona"},
            {"ingrediente": "Limón",            "supermercado": "Cualquiera"},
            {"ingrediente": "Calabacín",        "supermercado": "Cualquiera"},
            {"ingrediente": "Caldo de verduras","supermercado": "Mercadona"},
            {"ingrediente": "Champiñones",      "supermercado": "Consum"},
            {"ingrediente": "Atún en lata",     "supermercado": "Mercadona"},
            {"ingrediente": "Lechuga",          "supermercado": "Consum"},
            {"ingrediente": "Tomate",           "supermercado": "Cualquiera"},
        ]).execute()

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Cesta App", page_icon="🛒", layout="wide")

try:
    init_data()
except Exception as e:
    st.error(f"Error al conectar con Supabase: {e}")
    st.stop()

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

    default_personas = 2
    if not plan_df.empty and "personas" in plan_df.columns:
        vals = plan_df["personas"].dropna()
        if not vals.empty:
            default_personas = int(vals.iloc[0])
    default_personas = st.number_input(
        "👥 Personas por defecto", min_value=1, max_value=20, value=default_personas,
        help="Se aplicará a todas las comidas. Puedes cambiarlo individualmente en cada una."
    )

    st.markdown("---")

    opciones_comida = ["— sin planificar —"] + sorted(
        comidas_df[comidas_df["comida"] == True]["nombre"].tolist()
    )
    opciones_cena = ["— sin planificar —"] + sorted(
        comidas_df[comidas_df["cena"] == True]["nombre"].tolist()
    )

    # Lookup de comida y personas guardadas
    plan_lookup = {}
    personas_lookup = {}
    for _, row in plan_df.iterrows():
        plan_lookup[(row["fecha"], row["tipo"])]    = row["comida"]
        personas_lookup[(row["fecha"], row["tipo"])]= int(row["personas"])

    today = date.today()
    dias  = [today + timedelta(days=i) for i in range(10)]
    selections = {}  # (fecha, tipo) -> (comida, personas)

    for d in dias:
        st.markdown(f"**📅 {format_fecha(d)}**")
        c1, c2, c3, c4 = st.columns([4, 1, 4, 1])
        with c1:
            prev = plan_lookup.get((d, "comida"), "— sin planificar —")
            idx  = opciones_comida.index(prev) if prev in opciones_comida else 0
            comida_sel = st.selectbox("🍽️ Comida", opciones_comida, index=idx, key=f"c_{d}")
        with c2:
            p_comida = st.number_input(
                "👥", min_value=1, max_value=20,
                value=personas_lookup.get((d, "comida"), default_personas),
                key=f"pc_{d}"
            )
        with c3:
            prev = plan_lookup.get((d, "cena"), "— sin planificar —")
            idx  = opciones_cena.index(prev) if prev in opciones_cena else 0
            cena_sel = st.selectbox("🌙 Cena", opciones_cena, index=idx, key=f"ce_{d}")
        with c4:
            p_cena = st.number_input(
                "👥", min_value=1, max_value=20,
                value=personas_lookup.get((d, "cena"), default_personas),
                key=f"pce_{d}"
            )
        selections[(d, "comida")] = (comida_sel, p_comida)
        selections[(d, "cena")]   = (cena_sel,   p_cena)
        st.markdown("---")

    if st.button("💾 Guardar planificación", type="primary"):
        rows = [
            {"fecha": str(d), "tipo": tipo, "comida": comida, "personas": int(pers)}
            for (d, tipo), (comida, pers) in selections.items()
            if comida != "— sin planificar —"
        ]
        sb = get_client()
        sb.table("planificacion").delete().gte("id", 0).execute()
        if rows:
            sb.table("planificacion").insert(rows).execute()
        st.success("✅ Planificación guardada.")
        st.cache_data.clear()

# ===========================================================================
# PÁGINA: LISTA DE LA COMPRA
# ===========================================================================
elif page == "🛍️ Lista de la compra":
    st.title("🛍️ Lista de la compra")

    plan_df         = load_planificacion()
    recetas_df      = load_table("recetas")
    ingredientes_df = load_table("ingredientes")

    if plan_df.empty:
        st.warning("No hay planificación guardada. Ve primero a **Planificación**.")
        st.stop()

    n_personas = int(plan_df["personas"].dropna().iloc[0])
    st.info(f"Planificación para **{n_personas} persona(s)**")

    with st.expander("Ver planificación completa"):
        for d in sorted(plan_df["fecha"].dropna().unique()):
            filas  = plan_df[plan_df["fecha"] == d]
            comida = filas[filas["tipo"] == "comida"]["comida"].values
            cena   = filas[filas["tipo"] == "cena"]["comida"].values
            st.write(
                f"**{format_fecha(d)}** — "
                f"🍽️ {comida[0] if len(comida) else '—'} &nbsp;|&nbsp; "
                f"🌙 {cena[0] if len(cena) else '—'}"
            )

    st.markdown("---")

    shopping   = []
    sin_receta = []
    sin_super  = []

    for _, row in plan_df.iterrows():
        plato    = row["comida"]
        personas = int(row["personas"])
        receta   = recetas_df[recetas_df["comida"] == plato]

        if receta.empty:
            if plato not in sin_receta:
                sin_receta.append(plato)
            continue

        for _, ing in receta.iterrows():
            ingrediente  = ing["ingrediente"]
            cantidad     = float(ing["cantidad"]) * personas
            unidad       = ing["unidad"]
            store_row    = ingredientes_df[ingredientes_df["ingrediente"] == ingrediente]
            supermercado = store_row.iloc[0]["supermercado"] if not store_row.empty else "Sin asignar"
            if store_row.empty and ingrediente not in sin_super:
                sin_super.append(ingrediente)

            shopping.append({
                "ingrediente": ingrediente,
                "cantidad":    cantidad,
                "unidad":      unidad,
                "supermercado":supermercado,
            })

    if sin_receta:
        st.warning(f"⚠️ Sin receta: {', '.join(sin_receta)}")
    if sin_super:
        st.warning(f"⚠️ Sin supermercado: {', '.join(sin_super)}")

    if not shopping:
        st.info("No hay ingredientes que mostrar.")
        st.stop()

    agg = (
        pd.DataFrame(shopping)
        .groupby(["supermercado", "ingrediente", "unidad"], as_index=False)["cantidad"]
        .sum()
        .sort_values(["supermercado", "ingrediente"])
    )

    ORDEN  = ["Mercadona", "Consum", "Pescatería", "Carnicería", "Cualquiera", "Sin asignar"]
    ICONOS = {"Mercadona": "🟢", "Consum": "🔵", "Pescatería": "🐟",
              "Carnicería": "🥩", "Cualquiera": "⚪", "Sin asignar": "⚠️"}

    presentes = [s for s in ORDEN if s in agg["supermercado"].values]
    cols = st.columns(len(presentes))
    for i, super_name in enumerate(presentes):
        with cols[i]:
            st.subheader(f"{ICONOS[super_name]} {super_name}")
            for _, r in agg[agg["supermercado"] == super_name].iterrows():
                st.write(f"- {r['ingrediente']}: **{r['cantidad']:g} {r['unidad']}**")

# ===========================================================================
# PÁGINA: RECETAS
# ===========================================================================
elif page == "📖 Recetas":
    st.title("📖 Recetas")

    comidas_df = load_comidas()
    recetas_df = load_table("recetas")

    tab_ver, tab_platos = st.tabs(["Ingredientes por plato", "Gestionar platos"])

    with tab_ver:
        todos     = sorted(comidas_df["nombre"].tolist())
        plato_sel = st.selectbox("Selecciona un plato", todos)
        subset    = recetas_df[recetas_df["comida"] == plato_sel].copy().reset_index(drop=True)

        if subset.empty:
            st.info("Este plato aún no tiene receta.")

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
            otros = recetas_df[recetas_df["comida"] != plato_sel][["comida", "ingrediente", "cantidad", "unidad"]]
            nuevo = pd.concat([otros, edited[["comida", "ingrediente", "cantidad", "unidad"]]], ignore_index=True)
            save_table("recetas", nuevo)
            st.success("Receta guardada.")
            st.cache_data.clear()

    with tab_platos:
        st.markdown("Añade, edita o elimina platos del catálogo.")
        edited_comidas = st.data_editor(
            comidas_df[["nombre", "comida", "cena"]],
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "comida": st.column_config.CheckboxColumn("🍽️ Comida"),
                "cena":   st.column_config.CheckboxColumn("🌙 Cena"),
            },
        )
        if st.button("💾 Guardar platos"):
            edited_comidas = edited_comidas.dropna(subset=["nombre"])
            save_table("comidas", edited_comidas)
            st.success("Lista de platos actualizada.")
            st.cache_data.clear()

# ===========================================================================
# PÁGINA: INGREDIENTES
# ===========================================================================
elif page == "🏪 Ingredientes":
    st.title("🏪 Ingredientes y supermercados")

    ingredientes_df = load_table("ingredientes")

    st.markdown("Asigna cada ingrediente al supermercado donde lo compras habitualmente.")

    edited = st.data_editor(
        ingredientes_df[["ingrediente", "supermercado"]],
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "supermercado": st.column_config.SelectboxColumn(
                "Supermercado",
                options=["Mercadona", "Consum", "Pescatería", "Carnicería", "Cualquiera"]
            )
        },
    )

    if st.button("💾 Guardar", type="primary"):
        edited = edited.dropna(subset=["ingrediente"])
        save_table("ingredientes", edited)
        st.success("Lista de ingredientes actualizada.")
        st.cache_data.clear()
