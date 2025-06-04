# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

    
# Write directly to the app
st.title(f"Customise Your Smoothie! 🥤")
st.write(
  """Choose The Fruits You Want In Your Custom Smoothie !
  """
)

name_on_order = st.text_input("Name On Smoothie")
st.write("The Name Of Your Smoothie Will Be:",name_on_order )    

session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'))
st.dataframe(data=my_dataframe, use_container_width=True)

ingridients_list = st.multiselect(
    "Choose Up to 5 ingredients",
        my_dataframe,
        max_selections=5
)

if ingridients_list:
    
    ingredients_string = ''
    for fruit_chosen in ingridients_list:
        ingredients_string += fruit_chosen + ' '
    # st.write(fruit_chosen)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients , name_on_order)
            values ('""" + ingredients_string + """' , '""" + name_on_order + """' )"""

    st.write(my_insert_stmt)
    # st.stop()   
    
    time_to_insert = st.button('Submit Order')


    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")





