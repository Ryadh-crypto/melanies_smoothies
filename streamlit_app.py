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

# --- 🔽 Récupérer et afficher la nutrition des fruits choisis ---
if ingredients_list:
    st.subheader("Nutrition Info for Selected Fruits")
    
    nutrition_data = []
    
    for fruit in ingredients_list:
        # L'API SmoothieFroot semble sensible à la casse, on met en minuscule
        fruit_api_name = fruit.lower()
        
        url = f"https://my.smoothiefroot.com/api/fruit/{fruit_api_name}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                nutrition_data.append(data)
            else:
                st.warning(f"No data format issue for {fruit}")
        else:
            st.warning(f"Failed to fetch data for {fruit}")
    
    # Affichage des infos nutritionnelles sans pandas
    if nutrition_data:
        st.dataframe(nutrition_data, use_container_width=True)
    else:
        st.info("No nutrition data available for the selected fruits.")
