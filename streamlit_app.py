import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Connexion à Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Titre
st.title("Customise Your Smoothie! 🥤")

# Entrée nom
name_on_order = st.text_input("Name on Smoothie")

# Fruits depuis Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col("fruit_name"))
fruit_list = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

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

# --- 🔽 Partie API SmoothieFroot & sf_df ---
# Récupération des infos fruit depuis l'API externe
response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")

if response.status_code == 200:
    fruit_data = response.json()

    # Si le JSON est un dict, on l'encapsule dans une liste
    if isinstance(fruit_data, dict):
        sf_df = [fruit_data]  # ✅ streamlit accepte une liste de dictionnaires
    elif isinstance(fruit_data, list):
        sf_df = fruit_data
    else:
        sf_df = []

    # Affichage du DataFrame sans pandas
    st.subheader("🍉 Watermelon Info from SmoothieFroot API")
    st.dataframe(sf_df, use_container_width=True)
else:
    st.error("Failed to fetch watermelon info from SmoothieFroot API.")
