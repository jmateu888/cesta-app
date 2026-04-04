import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, timedelta

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
DIAS_ES  = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

SHEET_COMIDAS       = "comidas"
SHEET_RECETAS       = "recetas"
SHEET_INGREDIENTES  = "ingredientes"
SHEET_PLANIFICACION = "planificacion"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def format_fecha(d: date) -> str:
    return f"{DIAS_ES[d.weekday()]} {d.day} de {MESES_ES[d.month - 1]}"

# ---------------------------------------------------------------------------
# Conexión a Google Sheets
# ---------------------------------------------------------------------------
@st.cache_resource
def get_spreadsheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    gc = gspread.authorize(creds)
    return gc.open_by_key(st.secrets["sheets"]["spreadsheet_id"])

def get_ws(name: str):
    return get_spreadsheet().worksheet(name)

# ---------------------------------------------------------------------------
# Lectura / escritura de hojas
# ---------------------------------------------------------------------------
@st.cache_data(ttl=15)
def load_sheet(name: str) -> pd.DataFrame:
    ws = get_ws(name)
    records = ws.get_all_records(default_blank=None)
    return pd.DataFrame(records)

def save_sheet(name: str, df: pd.DataFrame):
    ws = get_ws(name)
    df = df.where(pd.notnull(df), None)          # NaN → None para Sheets
    ws.clear()
    ws.update([df.columns.tolist()] + df.values.tolist())

def load_comidas() -> pd.DataFrame:
    df = load_sheet(SHEET_COMIDAS)
    # Google Sheets devuelve booleanos como True/False directamente
    for col in ["comida", "cena"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda v: v is True or str(v).upper() == "TRUE")
    return df

def load_planificacion() -> pd.DataFrame:
    df = load_sheet(SHEET_PLANIFICACION)
    if not df.empty and "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce").dt.date
    return df

# ---------------------------------------------------------------------------
# Inicialización de hojas (solo si están vacías)
# ---------------------------------------------------------------------------
def init_sheets():
    sh = get_spreadsheet()
    existing = [ws.title for ws in sh.worksheets()]

    if SHEET_COMIDAS not in existing:
        ws = sh.add_worksheet(SHEET_COMIDAS, rows=100, cols=10)
        df = pd.DataFrame({
            "nombre": [
                "Paella de pollo", "Lentejas con chorizo", "Pasta boloñesa",
                "Tortilla de patatas", "Arroz al horno", "Pollo asado",
                "Ensalada mixta", "Gazpacho",
                "Crema de calabacín", "Huevos revueltos con champiñones",
                "Ensalada de atún", "Salmón a la plancha",
                "Croquetas caseras", "Verduras a la plancha con huevo",
            ],
            "comida": [True, True, True, True, True, True, True, True, False, False, True, False, False, False],
            "cena":   [False, False, True, True, False, True, True, True, True, True, True, True, True, True],
        })
        ws.update([df.columns.tolist()] + df.values.tolist())

    if SHEET_RECETAS not in existing:
        ws = sh.add_worksheet(SHEET_RECETAS, rows=200, cols=10)
        df = pd.DataFrame({
            "comida": [
                "Paella de pollo", "Paella de pollo", "Paella de pollo", "Paella de pollo",
                "Lentejas con chorizo", "Lentejas con chorizo", "Lentejas con chorizo",
                "Pasta boloñesa", "Pasta boloñesa", "Pasta boloñesa", "Pasta boloñesa",
                "Tortilla de patatas", "Tortilla de patatas",
                "Salmón a la plancha", "Salmón a la plancha",
                "Crema de calabacín", "Crema de calabacín", "Crema de calabacín",
                "Huevos revueltos con champiñones", "Huevos revueltos con champiñones",
                "Ensalada de atún", "Ensalada de atún", "Ensalada de atún",
            ],
            "ingrediente": [
                "Arroz", "Pollo", "Pimiento rojo", "Tomate frito",
                "Lentejas", "Chorizo", "Cebolla",
                "Pasta", "Carne picada", "Tomate frito", "Queso parmesano",
                "Patata", "Huevos",
                "Salmón", "Limón",
                "Calabacín", "Cebolla", "Caldo de verduras",
                "Huevos", "Champiñones",
                "Atún en lata", "Lechuga", "Tomate",
            ],
            "cantidad": [
                100, 300, 1, 200,
                150, 100, 1,
                100, 200, 200, 50,
                2, 3,
                200, 1,
                2, 1, 300,
                3, 200,
                2, 0.5, 2,
            ],
            "unidad": [
                "g", "g", "ud", "ml",
                "g", "g", "ud",
                "g", "g", "ml", "g",
                "ud", "ud",
                "g", "ud",
                "ud", "ud", "ml",
                "ud", "g",
                "lata", "ud", "ud",
            ],
        })
        ws.update([df.columns.tolist()] + df.values.tolist())

    if SHEET_INGREDIENTES not in existing:
        ws = sh.add_worksheet(SHEET_INGREDIENTES, rows=200, cols=10)
        df = pd.DataFrame({
            "ingrediente": [
                "Arroz", "Pollo", "Pimiento rojo", "Tomate frito",
                "Lentejas", "Chorizo", "Cebolla",
                "Pasta", "Carne picada", "Queso parmesano",
                "Patata", "Huevos",
                "Salmón", "Limón",
                "Calabacín", "Caldo de verduras",
                "Champiñones", "Atún en lata", "Lechuga", "Tomate",
            ],
            "supermercado": [
                "Mercadona", "Mercadona", "Consum", "Mercadona",
                "Consum", "Mercadona", "Cualquiera",
                "Consum", "Mercadona", "Consum",
                "Cualquiera", "Mercadona",
                "Mercadona", "Cualquiera",
                "Cualquiera", "Mercadona",
                "Consum", "Mercadona", "Consum", "Cualquiera",
            ],
        })
        ws.update([df.columns.tolist()] + df.values.tolist())

    if SHEET_PLANIFICACION not in existing:
        ws = sh.add_worksheet(SHEET_PLANIFICACION, rows=200, cols=10)
        ws.update([["fecha", "tipo", "comida", "personas"]])

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Cesta App", page_icon="🛒", layout="wide")

try:
    init_sheets()
except Exception as e:
    st.error(f"Error al conectar con Google Sheets: {e}")
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
        default_personas = int(plan_df["personas"].dropna().iloc[0]) if not plan_df["personas"].dropna().empty else 2
    personas = st.number_input("👥 Número de personas", min_value=1, max_value=20, value=default_personas)

    st.markdown("---")

    opciones_comida = ["— sin planificar —"] + sorted(
        comidas_df[comidas_df["comida"] == True]["nombre"].tolist()
    )
    opciones_cena = ["— sin planificar —"] + sorted(
        comidas_df[comidas_df["cena"] == True]["nombre"].tolist()
    )

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

    if st.button("💾 Guardar planificación", type="primary"):
        rows = [
            {"fecha": str(d), "tipo": tipo, "comida": comida, "personas": int(personas)}
            for (d, tipo), comida in selections.items()
            if comida != "— sin planificar —"
        ]
        save_sheet(SHEET_PLANIFICACION, pd.DataFrame(rows))
        st.success("✅ Planificación guardada.")
        st.cache_data.clear()

# ===========================================================================
# PÁGINA: LISTA DE LA COMPRA
# ===========================================================================
elif page == "🛍️ Lista de la compra":
    st.title("🛍️ Lista de la compra")

    plan_df         = load_planificacion()
    recetas_df      = load_sheet(SHEET_RECETAS)
    ingredientes_df = load_sheet(SHEET_INGREDIENTES)

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

    shopping      = []
    sin_receta    = []
    sin_super     = []

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
            cantidad    = float(ing["cantidad"]) * personas
            unidad      = ing["unidad"]
            store_row   = ingredientes_df[ingredientes_df["ingrediente"] == ingrediente]

            if store_row.empty:
                if ingrediente not in sin_super:
                    sin_super.append(ingrediente)
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
        subset = agg[agg["supermercado"] == super_name]
        with cols[i]:
            st.subheader(f"{ICONOS[super_name]} {super_name}")
            for _, r in subset.iterrows():
                st.write(f"- {r['ingrediente']}: **{r['cantidad']:g} {r['unidad']}**")

# ===========================================================================
# PÁGINA: RECETAS
# ===========================================================================
elif page == "📖 Recetas":
    st.title("📖 Recetas")

    comidas_df = load_comidas()
    recetas_df = load_sheet(SHEET_RECETAS)

    tab_ver, tab_platos = st.tabs(["Ingredientes por plato", "Gestionar platos"])

    with tab_ver:
        todos = sorted(comidas_df["nombre"].tolist())
        plato_sel = st.selectbox("Selecciona un plato", todos)

        subset = recetas_df[recetas_df["comida"] == plato_sel].copy().reset_index(drop=True)

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
            otros = recetas_df[recetas_df["comida"] != plato_sel]
            nuevo = pd.concat(
                [otros, edited[["comida", "ingrediente", "cantidad", "unidad"]]],
                ignore_index=True
            )
            save_sheet(SHEET_RECETAS, nuevo)
            st.success("Receta guardada.")
            st.cache_data.clear()

    with tab_platos:
        st.markdown("Añade, edita o elimina platos del catálogo.")
        edited_comidas = st.data_editor(
            comidas_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "comida": st.column_config.CheckboxColumn("🍽️ Comida"),
                "cena":   st.column_config.CheckboxColumn("🌙 Cena"),
            },
        )
        if st.button("💾 Guardar platos"):
            edited_comidas = edited_comidas.dropna(subset=["nombre"])
            save_sheet(SHEET_COMIDAS, edited_comidas)
            st.success("Lista de platos actualizada.")
            st.cache_data.clear()

# ===========================================================================
# PÁGINA: INGREDIENTES
# ===========================================================================
elif page == "🏪 Ingredientes":
    st.title("🏪 Ingredientes y supermercados")

    ingredientes_df = load_sheet(SHEET_INGREDIENTES)

    st.markdown("Asigna cada ingrediente al supermercado donde lo compras habitualmente.")

    edited = st.data_editor(
        ingredientes_df,
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
        save_sheet(SHEET_INGREDIENTES, edited)
        st.success("Lista de ingredientes actualizada.")
        st.cache_data.clear()
