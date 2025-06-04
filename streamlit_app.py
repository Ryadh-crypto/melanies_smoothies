# Import des packages nécessaires
import streamlit as st
import request
from snowflake.snowpark.functions import col

# Connexion à Snowflake (assure-toi que secrets.toml est bien configuré)
cnx = st.connection("snowflake")
session = cnx.session()


# Titre de l'application
st.title("Customise Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie!")

# Entrée utilisateur pour le nom de la commande
name_on_order = st.text_input("Name on Smoothie")

# Chargement et affichage des fruits disponibles
my_dataframe = session.table("smoothies.public.fruit_options").select(col("fruit_name"))
st.write("Available fruits:")
st.dataframe(my_dataframe, use_container_width=True)

# ⚠️ ATTENTION : Snowflake renvoie les noms de colonnes en MAJUSCULES
fruit_list = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Sélection d'ingrédients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients",
    fruit_list,
    max_selections=5
)

# Si des ingrédients sont sélectionnés, on prépare l'insertion
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


smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response)

