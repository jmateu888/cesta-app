from supabase import create_client, Client
import pandas as pd
import tomllib
from pathlib import Path

secrets_path = Path(__file__).parent.parent / ".streamlit" / "secrets.toml"
with open(secrets_path, "rb") as f:
    secrets = tomllib.load(f)

url = secrets["supabase"]["url"]
key = secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# Varias tablas
df1 = pd.DataFrame(supabase.table("comidas").select("*").execute().data)
df2 = pd.DataFrame(supabase.table("ingredientes").select("*").execute().data)
df3 = pd.DataFrame(supabase.table("recetas").select("*").execute().data)
df4 = pd.DataFrame(supabase.table("supermercados").select("*").execute().data)
df5 = pd.DataFrame(supabase.table("planificacion").select("*").execute().data)