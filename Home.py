# streamlit: name = Home
import streamlit as st 
#from constant import *
import numpy as np 
import pandas as pd
from PIL import Image
import plotly.express as px
import os
import sys
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import base64
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Utils import Utils

#Leitura e limpeza dos dados
utils = Utils()
dataset_zomato = utils.read_dataset('./datasets/zomato.csv')
dataset_zomato = utils.clean_dataset(dataset_zomato)
df = dataset_zomato.copy()


st.set_page_config(page_title='Home' ,layout="wide", page_icon='🍴')

st.header('Fome Zero!')
st.markdown('<p style="font-size:20px; color:gray; margin-top: -10px;">Data-Driven Food Insights</p>', unsafe_allow_html=True)

st.markdown("""
<p style="text-align: justify; font-size:16px;">
<b>Fome Zero</b> is a marketplace that connects customers to restaurants from different parts of the world.
Through its platform, restaurants can share information such as location, type of cuisine, available services, and customer ratings.
</p>

<p style="text-align: justify; font-size:16px;">
This dashboard was developed to support the company’s new management in understanding the current landscape of the platform,
offering strategic insights from three main perspectives: <b>Cities</b>, <b>Types of Cuisine</b>, and <b>Countries</b>.
</p>
""", unsafe_allow_html=True)


#====================================================
#Funções
#====================================================

def location_share(df):
    # Remover duplicatas de restaurante
    df_unique = df.drop_duplicates(subset='restaurant_id')

    # Criar mapa base
    mapa = folium.Map(zoom_start=2)
    cluster = MarkerCluster().add_to(mapa)

    # Adicionar cada restaurante ao cluster (granularidade automática)
    for _, row in df_unique.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=5,
            color='orange',
            fill=True,
            fill_opacity=0.6,
            tooltip=f"{row['restaurant_name']} - {row['city']} ({row['country']})"
        ).add_to(cluster)

    folium_static(mapa, width=1024, height=600)

def styled_metric(title, value):
    st.markdown(f"""
        <div style="
            background-color: #ffe4c4;
            padding: 16px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            font-family: 'Segoe UI', sans-serif;
            margin-bottom: 30px;
        ">
            <p style="margin:0; font-size:13px;">{title}</p>
            <p style="margin:8px 0 0 0; font-size:24px;"><b>{value}</b></p>
        </div>
    """, unsafe_allow_html=True)

def format_number(value):
    if pd.isna(value):
        return ""
    return f"{value:,.0f}".replace(",", ".")
    
#====================================================
#Barra Lateral
#====================================================

image_path = os.path.join('images', 'logo.png')
image = Image.open(image_path)
image_base64 = base64.b64encode(open(image_path, "rb").read()).decode()

st.sidebar.markdown(f"""
    <div style="display: flex; align-items: center;">
        <img src="data:image/png;base64,{image_base64}" width="30" style="margin-right: 10px;" />
        <h1 style="font-size: 20px; margin: 0;">Fome Zero</h1>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""Please choise filter""")

country_options = st.sidebar.multiselect(
    "Select Countries",
    list(df['country'].unique()),
    default=['Brazil', 'England', 'United States of America']
)

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

#Filtros
linhas_selecionadas = df['country'].isin( country_options )
df = df.loc[linhas_selecionadas,:]

#====================================================
#Layout Dashboard
#====================================================

with st.container():
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2.5, 2], gap='medium')
    with col1:
        qtd_restaurant = df['restaurant_id'].nunique()
        #col1.metric('Restaurants', locale.format_string('%.0f', qtd_restaurant, grouping=True))
        styled_metric('Restaurants', format_number(qtd_restaurant))

    with col2:
        country = df['country_code'].nunique()
        styled_metric('Countries', str(country))
    with col3:
        city = df['city'].nunique()
        styled_metric('Cities', str(city))
    with col4:
        review = df['votes'].sum()
        #col4.metric('Restaurant Reviews', str(review))
        styled_metric('Restaurant Reviews', format_number(review))
    with col5:
        review = df['cuisines'].nunique()
        styled_metric('Cuisines', str(review))
with st.container():
    location_share(df)
