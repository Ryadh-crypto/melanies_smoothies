import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Connexion à Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Titre
st.title("Customise Your Smoothie! 🥤")

# Entrée nom
name_on_order = st.text_input("Name on Smoothie")

# Récupérer fruit_name + search_on depuis la table
my_dataframe = session.table("smoothies.public.fruit_options").select(col("fruit_name"), col("search_on"))
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)
st.stop()
fruit_mapping = {row["FRUIT_NAME"]: row["SEARCH_ON"] for row in my_dataframe.collect()}  # Dict fruit affiché → nom API

# Liste des fruits affichés à l'utilisateur
fruit_list = list(fruit_mapping.keys())

# Sélection d'ingrédients
ingredients_list = st.multiselect("Choose up to 5 ingredients", fruit_list, max_selections=5)

# Commande
if ingredients_list and name_on_order:
    ingredients_string = ", ".join(ingredients_list)
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success("✅ Your Smoothie is ordered!")

# --- 🔽 Affichage nutrition pour les fruits choisis ---
if ingredients_list:
    st.subheader("Nutrition Info for Selected Fruits")
    
    unresolved_fruits = []  # Fruits introuvables même avec SEARCH_ON
    
    for fruit in ingredients_list:
        st.subheader(f"{fruit} Nutrition Information")

        # Utiliser le nom de recherche (sinon fallback en minuscule du nom affiché)
        fruit_api_name = fruit_mapping.get(fruit, fruit).lower()

        url = f"https://my.smoothiefroot.com/api/fruit/{fruit_api_name}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                st.dataframe([data], use_container_width=True)
            else:
                st.warning(f"No proper data format for {fruit}")
        else:
            st.warning(f"⚠️ Could not fetch nutrition data for {fruit} (searched as '{fruit_api_name}')")
            unresolved_fruits.append(fruit)

    # Afficher les fruits non trouvés pour info à Melanie
    if unresolved_fruits:
        st.info("The following fruits could not be resolved. Melanie may need to be informed:")
        st.write(unresolved_fruits)
