import pandas as pd
import streamlit as st
import altair as alt
from streamlit_player import st_player
import os
import numpy as np 
import pandas as pd
import os
import sys
import altair as alt
import base64
from PIL import Image
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Utils import Utils

#Leitura e limpeza dos dados
utils = Utils()
dataset_zomato = utils.read_dataset('./datasets/zomato.csv')
dataset_zomato = utils.clean_dataset(dataset_zomato)
df = dataset_zomato.copy()

#====================================================
#Funções
#====================================================

def qtd_city_country(df):
    columns = ['city', 'country']
    kpi_country_city = df[columns].groupby('country').nunique().reset_index()
    kpi_country_city.columns = ['country', 'qtd']
    kpi_country_city = kpi_country_city.sort_values('qtd', ascending=False).reset_index(drop=True)

    # Captura a ordem correta para forçar o Altair a seguir
    ordered_countries = kpi_country_city['country'].tolist()

    # Gráfico base com cores laranja
    base = alt.Chart(kpi_country_city).encode(
        x=alt.X('country:N',
                sort=ordered_countries,
                title='',
                axis=alt.Axis(labelAngle=0, labelColor='black')),
        y=alt.Y('qtd:Q',
                title='',
                axis=alt.Axis(labels=False, ticks=False, domain=False, grid=False)),
        color=alt.Color('qtd:Q', scale=alt.Scale(scheme='oranges'), legend=None)
    )

    bars = base.mark_bar()

    # Texto com cor preta e ordenação mantida
    text = alt.Chart(kpi_country_city).mark_text(
        align='center',
        baseline='bottom',
        dy=-2,
        fontSize=12,
        color='black'
    ).encode(
        x=alt.X('country:N', sort=ordered_countries),
        y='qtd:Q',
        text='qtd:Q'
    )

    fig = (bars + text).properties(
        title='Number of Cities by Country'
    )

    return fig


def qtd_restaurant_country(df):
    # Agrupar por país e contar restaurantes únicos
    columns = ['restaurant_name', 'country']
    kpi_country_restaurant = df[columns].groupby('country').nunique().reset_index()
    kpi_country_restaurant.columns = ['country', 'qtd']
    kpi_country_restaurant = kpi_country_restaurant.sort_values('qtd', ascending=False).reset_index(drop=True)

    # Capturar a ordem para garantir ordenação correta
    ordered_countries = kpi_country_restaurant['country'].tolist()

    # Gráfico base com cores laranja
    base = alt.Chart(kpi_country_restaurant).encode(
        x=alt.X('country:N', 
                sort=ordered_countries, 
                title='', 
                axis=alt.Axis(labelAngle=0, labelColor='black')),
        y=alt.Y('qtd:Q', 
                title='', 
                axis=alt.Axis(labels=False, ticks=False, domain=False, grid=False)),
        color=alt.Color('qtd:Q', scale=alt.Scale(scheme='oranges'), legend=None)
    )

    # Barras
    bars = base.mark_bar()

    # Rótulos
    text = alt.Chart(kpi_country_restaurant).mark_text(
        align='center',
        baseline='bottom',
        dy=-2,
        fontSize=12,
        color='black'
    ).encode(
        x=alt.X('country:N', sort=ordered_countries),
        y='qtd:Q',
        text='qtd:Q'
    )

    # Combinar barra e rótulo
    fig = (bars + text).properties(
        title='Number of Restaurants by Country'
    )

    return fig


def style_table(
    df,
    col_formatadas=None,
    col_gradiente=None,
    cmap='Oranges',
    font_size='14px',
    header_bg='#FFE4C4'
):
    styled = df.style

    # Formatação
    if col_formatadas:
        styled = styled.format(col_formatadas)
    if col_gradiente:
        styled = styled.background_gradient(subset=col_gradiente, cmap=cmap)

    # Aplicar estilo para esconder bordas completamente
    styled = styled.set_table_styles([
        {
            'selector': 'th',
            'props': [
                ('color', 'black'),
                ('background-color', header_bg),
                ('font-size', font_size),
                ('padding', '6px'),
                ('border', '0px solid transparent')
            ]
        },
        {
            'selector': 'td',
            'props': [
                ('font-size', font_size),
                ('padding', '6px'),
                ('border', 'none')
            ]
        },
        {
            'selector': 'table',
            'props': [
                ('border-collapse', 'collapse'),
                ('border', 'none'),
                ('width', '100%')
            ]
        }
    ], overwrite=True)

    return styled


def table_avg_country_cost_two(df):
    # Agrupando e calculando a média de custo para dois por país
    columns = ['average_cost_for_two', 'country']
    kpi_avg_country_cost_two = (
        df[columns]
        .groupby('country')
        .mean()
        .reset_index()
        .rename(columns={
            'country': 'Country',
            'average_cost_for_two': 'Mean Cost for Two'
        })
        .sort_values('Mean Cost for Two', ascending=False)
        .reset_index(drop=True)
    )


    styled_table = style_table(
    kpi_avg_country_cost_two,
    col_formatadas={'Mean Cost for Two': '{:.2f}'},
    col_gradiente=['Mean Cost for Two'],
    cmap='Oranges',
    )
    
    html_table = styled_table.hide(axis='index').to_html()
    
    scrollable_table = f"""
    <div style="max-height: 400px; overflow-y: auto;">
        {html_table}
    
    """
    
    st.markdown('<p style="font-size:16px; font-weight:bold;">Mean Cost for Two by Country</p>', unsafe_allow_html=True)
    st.markdown(scrollable_table, unsafe_allow_html=True)


def table_avg_country_votes(df):
    columns = ['aggregate_rating', 'country']
    kpi_avg_country_votes = (
        df[columns]
        .groupby('country')
        .mean()
        .reset_index()
        .rename(columns={
            'country': 'Country',
            'aggregate_rating': 'Mean Rating'
        })
        .sort_values('Mean Rating', ascending=False)
        .reset_index(drop=True)
    )
    
    # Título da tabela
    st.markdown('<p style="font-size:16px; font-weight:bold;">Mean Rating by Country</p>', unsafe_allow_html=True)
    
    # Aplica estilo reutilizável
    styled_df = style_table(
        df=kpi_avg_country_votes,
        col_formatadas={'Mean Rating': '{:.2f}'},
        col_gradiente=['Mean Rating'],
        cmap='Oranges'
    )

    # Converte para HTML ocultando índice
    html_table = styled_df.hide(axis='index').to_html()

    # Exibir com scroll
    st.markdown(f"""
        <div style="max-height: 400px; overflow-y: auto;">
            {html_table}

    """, unsafe_allow_html=True)


def table_qtd_country_cuisines(df):
    columns = ['cuisines', 'country']
    kpi_country_cuisines = (
        df[columns]
        .groupby('country')
        .nunique()
        .reset_index()
        .rename(columns={
            'country': 'Country',
            'cuisines': 'Qty Cuisines'
        })
        .sort_values('Qty Cuisines', ascending=False)
        .reset_index(drop=True)
    )
    
    # Título da tabela
    st.markdown('<p style="font-size:16px; font-weight:bold;">Qty Cuisines per Country</p>', unsafe_allow_html=True)
    
    # Aplica estilo reutilizável
    styled_df = style_table(
        df=kpi_country_cuisines,
        col_gradiente=['Qty Cuisines'],
        cmap='Oranges'
    )

    # Converte para HTML ocultando índice
    html_table = styled_df.hide(axis='index').to_html()

    # Exibir com scroll
    st.markdown(f"""
        <div style="max-height: 400px; overflow-y: auto;">
            {html_table}

    """, unsafe_allow_html=True)

        



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


price_options = st.sidebar.multiselect(
    "Select Price Tye",
    list(df['price_tye'].unique()),
    default=list(df['price_tye'].unique())
)

rating_options = st.sidebar.multiselect(
    "Select Rating Restaurant",
    list(df['type_rating'].unique()),
    default=list(df['type_rating'].unique())
)

delivery_options = st.sidebar.multiselect(
    "Do Delivery?",
    list(df['delivery'].unique()),
    default=list(df['delivery'].unique())
)

booking_options = st.sidebar.multiselect(
    "Do Table Booking?",
    list(df['booking'].unique()),
    default=list(df['booking'].unique())
)

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

#Filtros
linhas_selecionadas = df['country'].isin( country_options )
df = df.loc[linhas_selecionadas,:]

linhas_selecionadas = df['price_tye'].isin( price_options )
df = df.loc[linhas_selecionadas,:]

linhas_selecionadas = df['type_rating'].isin( rating_options )
df = df.loc[linhas_selecionadas,:]

linhas_selecionadas = df['delivery'].isin( delivery_options )
df = df.loc[linhas_selecionadas,:]

linhas_selecionadas = df['booking'].isin( booking_options )
df = df.loc[linhas_selecionadas,:]


st.header('🌎 Country')
st.markdown('<hr style="border:0.2px solid #F5F5F5; margin: 15px 0;">', unsafe_allow_html=True)


#====================================================
#Layout Dashboard
#====================================================
     
with st.container():
    fig = qtd_city_country(df)
    st.altair_chart(fig, use_container_width=True)

with st.container():
    fig = qtd_restaurant_country(df)
    st.altair_chart(fig, use_container_width=True)

with st.container():
    col1, col2, col3 = st.columns(3, gap='large')
    with col1:
        table_avg_country_votes(df)
    with col2:
        table_avg_country_cost_two(df) 
    with col3:
        table_qtd_country_cuisines(df) 



