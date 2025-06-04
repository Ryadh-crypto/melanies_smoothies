# Import des packages nécessaires
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Connexion à Snowflake (assure-toi que secrets.toml est bien configuré)
cnx = st.connection("snowflake")
session = cnx.session()

# Titre de l'application
st.title("Customise Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie!")

# Entrée utilisateur pour le nom de la commande
name_on_order = st.text_input("Name on Smoothie")

# Chargement et affichage des fruits disponibles avec search term
fruit_df = session.table("smoothies.public.fruit_options").select(col("fruit_name"), col("search_on"))
fruit_rows = fruit_df.collect()

# ⚠️ ATTENTION : Snowflake renvoie les noms de colonnes en MAJUSCULES
# Création d'un dictionnaire {affichage: search_term}
fruit_lookup = {row["FRUIT_NAME"]: row["SEARCH_ON"] for row in fruit_rows}

st.write("Available fruits:")
st.dataframe(fruit_rows, use_container_width=True)

# Liste des fruits affichés dans le multiselect
fruit_list = list(fruit_lookup.keys())

# Sélection d'ingrédients (max 5)
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients",
    fruit_list,
    max_selections=5
)

# Si des ingrédients sont sélectionnés et nom renseigné, on prépare l'insertion
if ingredients_list and name_on_order:
    ingredients_string = ", ".join(ingredients_list)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    st.write("SQL Statement to be executed:")
    st.code(my_insert_stmt, language="sql")

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success("✅ Your Smoothie is ordered!")

# --- 🔽 Partie API SmoothieFroot & affichage des infos fruits sélectionnés ---

st.subheader("Fruit Info from SmoothieFroot API")

for fruit_display_name in ingredients_list:
    # Récupérer le terme de recherche correspondant
    search_term = fruit_lookup.get(fruit_display_name, fruit_display_name)

    # Appel API (en minuscule)
    url = f"https://my.smoothiefroot.com/api/fruit/{search_term.lower()}"
    response = requests.get(url)

    if response.status_code == 200:
        fruit_data = response.json()

        # Si le JSON est un dict, on l'encapsule dans une liste pour st.dataframe
        if isinstance(fruit_data, dict):
            sf_df = [fruit_data]
        elif isinstance(fruit_data, list):
            sf_df = fruit_data
        else:
            sf_df = []

        st.markdown(f"### 🍓 {fruit_display_name}")
        st.dataframe(sf_df, use_container_width=True)
    else:
        st.warning(f"No data found for '{fruit_display_name}' using search term '{search_term}'.")
