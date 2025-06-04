# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Connexion à Snowflake via secrets.toml
cnx = st.connection('snowflake')
session = cnx.session()

# Titre et instructions
st.title("Customise Your Smoothie! 🥤")
st.write("Choose The Fruits You Want In Your Custom Smoothie !")

# Champ pour le nom
name_on_order = st.text_input("Name On Smoothie")
st.write("The Name Of Your Smoothie Will Be:", name_on_order)    

# Récupération des fruits disponibles
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'))
st.dataframe(data=my_dataframe, use_container_width=True)
st.write("Prévisualisation du DataFrame :")
st.dataframe(my_dataframe)

# Sélection d'ingrédients
fruit_list = [row["fruit_name"] for row in my_dataframe.collect()]  # Convertir DataFrame en liste
ingredients_list = st.multiselect(
    "Choose Up to 5 ingredients",
    fruit_list,
    max_selections=5
)

# Création de la commande
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    st.write(my_insert_stmt)
    
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
