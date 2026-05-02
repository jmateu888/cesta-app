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
# Columnas por defecto para cada tabla (evita KeyError cuando están vacías)
COLUMNAS = {
    "comidas":        ["nombre", "comida", "cena"],
    "recetas":        ["comida", "ingrediente", "cantidad", "unidad"],
    "ingredientes":   ["ingrediente", "supermercado", "marca"],
    "planificacion":  ["fecha", "tipo", "comida", "personas"],
    "supermercados":  ["nombre"],
}

# ---------------------------------------------------------------------------
@st.cache_data(ttl=15)
def load_table(name: str) -> pd.DataFrame:
    sb = get_client()
    response = sb.table(name).select("*").execute()
    if response.data:
        return pd.DataFrame(response.data)
    return pd.DataFrame(columns=COLUMNAS.get(name, []))

def save_table(name: str, df: pd.DataFrame):
    sb = get_client()
    sb.table(name).delete().gte("id", 0).execute()
    if not df.empty:
        df = df.drop(columns=["id"], errors="ignore")
        df = df.where(pd.notnull(df), None)  # NaN → None para que JSON lo acepte
        records = [{k: (None if v != v else v) for k, v in row.items()} for row in df.to_dict("records")]
        sb.table(name).insert(records).execute()

def load_comidas() -> pd.DataFrame:
    df = load_table("comidas")
    for col in ["comida", "cena"]:
        if col in df.columns:
            df[col] = df[col].astype(bool)
    return df

def load_planificacion() -> pd.DataFrame:
    df = load_table("planificacion")
    if not df.empty:
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

    c1, c2 = st.columns(2)
    with c1:
        num_dias = st.number_input("📅 Días a planificar", min_value=1, max_value=30, value=10)
    with c2:
        pass

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

    opciones_comida = ["— sin planificar —"] + sorted(comidas_df[comidas_df["comida"] == True]["nombre"].tolist())
    opciones_cena   = ["— sin planificar —"] + sorted(comidas_df[comidas_df["cena"]   == True]["nombre"].tolist())

    plan_lookup = {}
    personas_lookup = {}
    for _, row in plan_df.iterrows():
        plan_lookup[(row["fecha"], row["tipo"])]     = row["comida"]
        personas_lookup[(row["fecha"], row["tipo"])] = int(row["personas"])

    today = date.today()
    dias  = [today + timedelta(days=i) for i in range(num_dias)]
    selections    = {}
    opciones_personas = list(range(1, 21))

    for d in dias:
        st.markdown(f"**📅 {format_fecha(d)}**")
        c1, c2 = st.columns(2)
        with c1:
            prev = plan_lookup.get((d, "comida"), "— sin planificar —")
            idx  = opciones_comida.index(prev) if prev in opciones_comida else 0
            comida_sel = st.selectbox("🍽️ Comida", opciones_comida, index=idx, key=f"c_{d}")
            p_prev   = personas_lookup.get((d, "comida"), default_personas)
            p_comida = st.selectbox("👥", opciones_personas,
                index=opciones_personas.index(p_prev) if p_prev in opciones_personas else default_personas - 1,
                key=f"pc_{d}")
        with c2:
            prev = plan_lookup.get((d, "cena"), "— sin planificar —")
            idx  = opciones_cena.index(prev) if prev in opciones_cena else 0
            cena_sel = st.selectbox("🌙 Cena", opciones_cena, index=idx, key=f"ce_{d}")
            p_prev  = personas_lookup.get((d, "cena"), default_personas)
            p_cena  = st.selectbox("👥", opciones_personas,
                index=opciones_personas.index(p_prev) if p_prev in opciones_personas else default_personas - 1,
                key=f"pce_{d}")
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

    shop_df = pd.DataFrame(shopping)
    shop_df["unidad"] = shop_df["unidad"].fillna("")
    agg = (
        shop_df
        .groupby(["supermercado", "ingrediente", "unidad"], as_index=False)["cantidad"]
        .sum()
        .sort_values(["supermercado", "ingrediente"])
    )

    ICONOS_DEFAULT = {"Mercadona": "🟢", "Consum": "🔵", "Pescatería": "🐟",
                      "Carnicería": "🥩", "Cualquiera": "⚪", "Sin asignar": "⚠️"}

    todos_supers = sorted(agg["supermercado"].unique().tolist())

    if not todos_supers:
        st.info("No hay ingredientes con supermercado asignado.")
        st.stop()

    if "lista_edicion" not in st.session_state:
        st.session_state.lista_edicion = False

    # ── MODO VISTA ────────────────────────────────────────────────────────────
    if not st.session_state.lista_edicion:
        if st.button("✏️ Editar cantidades"):
            st.session_state.lista_edicion = True
            st.rerun()

        for super_name in todos_supers:
            icono = ICONOS_DEFAULT.get(super_name, "🏪")
            st.subheader(f"{icono} {super_name}")
            subset = agg[agg["supermercado"] == super_name]
            for _, r in subset.iterrows():
                cantidad_final = st.session_state.get(f"qty_{r['supermercado']}_{r['ingrediente']}", r["cantidad"])
                st.markdown(f"- {r['ingrediente']}: **{cantidad_final:g} {r['unidad']}**")
            st.divider()

    # ── MODO EDICIÓN ──────────────────────────────────────────────────────────
    else:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 Guardar y volver", type="primary"):
                st.session_state.lista_edicion = False
                st.rerun()
        with c2:
            if st.button("🔄 Restablecer cantidades"):
                for _, r in agg.iterrows():
                    key = f"qty_{r['supermercado']}_{r['ingrediente']}"
                    st.session_state[key] = r["cantidad"]
                st.session_state.lista_edicion = False
                st.rerun()

        for super_name in todos_supers:
            icono = ICONOS_DEFAULT.get(super_name, "🏪")
            st.subheader(f"{icono} {super_name}")
            subset = agg[agg["supermercado"] == super_name]
            for _, r in subset.iterrows():
                key     = f"qty_{r['supermercado']}_{r['ingrediente']}"
                if key not in st.session_state:
                    st.session_state[key] = r["cantidad"]
                unidad  = r["unidad"]
                step    = 50.0 if unidad in ["g", "ml"] else 1.0
                c1, c2, c3, c4 = st.columns([4, 1, 2, 1])
                with c1:
                    st.write(f"{r['ingrediente']}")
                with c2:
                    if st.button("➖", key=f"m_{key}", use_container_width=True):
                        st.session_state[key] = max(0.0, st.session_state[key] - step)
                        st.rerun()
                with c3:
                    st.write(f"**{st.session_state[key]:g} {unidad}**")
                with c4:
                    if st.button("➕", key=f"p_{key}", use_container_width=True):
                        st.session_state[key] += step
                        st.rerun()
            st.divider()

# ===========================================================================
# PÁGINA: RECETAS
# ===========================================================================
elif page == "📖 Recetas":
    st.title("📖 Recetas")

    comidas_df      = load_comidas()
    recetas_df      = load_table("recetas")
    ingredientes_df = load_table("ingredientes")

    opciones_ingredientes = sorted(ingredientes_df["ingrediente"].dropna().tolist()) if not ingredientes_df.empty else []

    tab_ver, tab_platos = st.tabs(["Ingredientes por plato", "Gestionar platos"])

    with tab_ver:
        todos     = sorted(comidas_df["nombre"].tolist())
        plato_sel = st.selectbox("Selecciona un plato", todos)
        subset    = recetas_df[recetas_df["comida"] == plato_sel].copy().reset_index(drop=True)

        if subset.empty:
            st.info("Este plato aún no tiene receta.")

        if not opciones_ingredientes:
            st.warning("Primero añade ingredientes en la sección 🏪 Ingredientes.")

        edited = st.data_editor(
            subset[["ingrediente", "cantidad", "unidad"]] if not subset.empty
            else pd.DataFrame(columns=["ingrediente", "cantidad", "unidad"]),
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "ingrediente": st.column_config.SelectboxColumn(
                    "Ingrediente", options=opciones_ingredientes
                ),
                "unidad": st.column_config.SelectboxColumn(
                    "Unidad", options=["g", "kg", "ml", "l", "ud", "lata", "cucharada"]
                ),
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
        if comidas_df.empty or "nombre" not in comidas_df.columns:
            comidas_df = pd.DataFrame(columns=["nombre", "comida", "cena"])
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

    tab_ing, tab_renombrar, tab_super = st.tabs(["Ingredientes", "Renombrar ingrediente", "Gestionar supermercados"])

    with tab_ing:
        ingredientes_df   = load_table("ingredientes")
        supermercados_df  = load_table("supermercados")

        if ingredientes_df.empty or "ingrediente" not in ingredientes_df.columns:
            ingredientes_df = pd.DataFrame(columns=["ingrediente", "supermercado", "marca"])
        if "marca" not in ingredientes_df.columns:
            ingredientes_df["marca"] = None

        opciones_super = sorted(supermercados_df["nombre"].tolist()) if not supermercados_df.empty else []

        st.markdown("Asigna cada ingrediente al supermercado donde lo compras habitualmente.")
        edited = st.data_editor(
            ingredientes_df[["ingrediente", "supermercado", "marca"]],
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "supermercado": st.column_config.SelectboxColumn(
                    "Supermercado", options=opciones_super
                ),
                "marca": st.column_config.TextColumn("Marca (opcional)"),
            },
        )

        if st.button("💾 Guardar", type="primary"):
            edited = edited.dropna(subset=["ingrediente"])
            save_table("ingredientes", edited)
            st.success("Lista de ingredientes actualizada.")
            st.cache_data.clear()

    with tab_renombrar:
        ingredientes_df2 = load_table("ingredientes")
        opciones_renombrar = sorted(ingredientes_df2["ingrediente"].dropna().tolist()) if not ingredientes_df2.empty else []

        if not opciones_renombrar:
            st.info("No hay ingredientes para renombrar.")
        else:
            st.markdown("Renombra un ingrediente y se actualizará automáticamente en las recetas.")
            ing_actual = st.selectbox("Ingrediente a renombrar", opciones_renombrar, key="ing_renombrar")
            ing_nuevo  = st.text_input("Nuevo nombre", value=ing_actual, key="ing_nuevo")

            if st.button("✏️ Renombrar", type="primary"):
                if ing_nuevo and ing_nuevo != ing_actual:
                    sb = get_client()
                    sb.table("ingredientes").update({"ingrediente": ing_nuevo}).eq("ingrediente", ing_actual).execute()
                    sb.table("recetas").update({"ingrediente": ing_nuevo}).eq("ingrediente", ing_actual).execute()
                    st.success(f"'{ing_actual}' renombrado a '{ing_nuevo}' en ingredientes y recetas.")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.warning("El nombre nuevo debe ser distinto al actual.")

    with tab_super:
        supermercados_df = load_table("supermercados")
        if supermercados_df.empty or "nombre" not in supermercados_df.columns:
            supermercados_df = pd.DataFrame(columns=["nombre"])

        st.markdown("Añade o elimina supermercados. Se usarán como opciones en la lista de ingredientes.")
        edited_super = st.data_editor(
            supermercados_df[["nombre"]],
            num_rows="dynamic",
            use_container_width=True,
            column_config={"nombre": st.column_config.TextColumn("Supermercado")},
        )

        if st.button("💾 Guardar supermercados", type="primary"):
            edited_super = edited_super.dropna(subset=["nombre"])
            save_table("supermercados", edited_super)
            st.success("Lista de supermercados actualizada.")
            st.cache_data.clear()
