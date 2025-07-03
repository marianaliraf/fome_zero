import pandas as pd
import streamlit as st
import altair as alt
import plotly.express as px
import os
import sys
import base64
from PIL import Image
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Utils import Utils

#Leitura e limpeza dos dados
utils = Utils()
dataset_zomato = utils.read_dataset('./datasets/zomato.csv')
dataset_zomato = utils.clean_dataset(dataset_zomato)
df = dataset_zomato.copy()

st.set_page_config(layout="wide")

#====================================================
#Funções
#====================================================

def barplot_custom(df, x, y, color, title, top_n, subtitle=None):
    # Ordenar e pegar os top N
    df_sorted = df.sort_values(by=y, ascending=False).head(top_n)

    # Define título com ou sem subtítulo
    full_title = f"<b>{title}</b>"
    if subtitle:
        full_title += f"<br><sub>{subtitle}</sub>"

    fig = px.bar(
        df_sorted,
        x=x,
        y=y,
        color=color,
        text=y,
        labels={x: '', y: '', color: ''},
        title=full_title,
        color_discrete_sequence=[
        '#8B0000',  # Dark Red (vinho)
        '#B22222',  # Firebrick
        '#D2691E',  # Chocolate
        '#CD853F',  # Peru
        '#FFA07A',  # Light Salmon
        '#FF8C00',  # Dark Orange
        '#FF4500',  # Orange Red
        '#A0522D',  # Sienna
        '#800000',  # Maroon
        '#E97451',  # Terra Cotta
        '#A52A2A',  # Brown
        '#DC143C',  # Crimson
        '#DEB887',  # Burlywood
        '#F4A460',  # Sandy Brown
        '#F08080'   # Light Coral
        ]
    )

    fig.update_traces(
        textposition='outside',
        textfont=dict(color='black'),
        cliponaxis=False
    )

    fig.update_layout(
        title={
            'x': 0,
            'xanchor': 'left',
            'font': {'color': 'black'},
            'text': full_title
        },
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(color='black')
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            tickfont=dict(color='black')
        ),
        margin=dict(t=100),
        height=400,
        autosize=True,
        uniformtext_minsize=10,
        uniformtext_mode='hide'
    )

    return fig


def top_city_qtd_restaurants(df):
    columns = ['city', 'restaurant_id', 'country']
    kpi_city_restaurant = df[columns].groupby(['city', 'country']).nunique().reset_index()
    
    kpi_city_restaurant.columns = ['city', 'country', 'qtd']
    
    kpi_city_restaurant = kpi_city_restaurant.sort_values('qtd', ascending=False).reset_index(drop=True).head(10)

    fig = barplot_custom(
    df=kpi_city_restaurant,
    x='city',
    y='qtd',
    color='country',
    title='Top 10 Cities by Number of Restaurant',
    top_n=10
    )
        
    return fig

def top_city_best_restaurants(df):
    columns = ['city', 'restaurant_id', 'country']
    df_aux = df[df['aggregate_rating'] > 4]
    
    kpi_city_best_restaurant = (
        df_aux[columns]
        .groupby(['city', 'country'])
        .nunique()
        .reset_index()
    )

    kpi_city_best_restaurant.columns = ['city', 'country', 'qtd']

    kpi_city_best_restaurant = (
        kpi_city_best_restaurant
        .sort_values('qtd', ascending=False)
        .reset_index(drop=True)
        .head(5)
    ) 

    fig = barplot_custom(
    df=kpi_city_best_restaurant,
    x='city',
    y='qtd',
    color='country',
    title='Top 5 Cities with the Most Rated Restaurants',
    subtitle='Considering only restaurants with ratings above 4.0',
    top_n=5
    )

    return fig

def top_city_worst_restaurant(df):
    columns = ['city', 'restaurant_id', 'country']

    df_aux = df.loc[df['aggregate_rating'] < 2.5]
    
    kpi_city_worst_restaurant = df_aux[columns].groupby(['city', 'country']).nunique().reset_index().head(5)
    
    kpi_city_worst_restaurant.columns = ['city', 'country', 'qtd']
    
    kpi_city_worst_restaurant = kpi_city_worst_restaurant.sort_values('qtd', ascending=False).reset_index(drop=True)

    fig = barplot_custom(
        df=kpi_city_worst_restaurant,
        x='city',
        y='qtd',
        color='country',
        title='Top 5 Cities with the Low Rated Restaurant',
        subtitle='Considering only restaurants with ratings under 2.5',
        top_n=5
    )
    return fig

def top_city_cuisines(df):
    columns = ['cuisines', 'city', 'country']

    kpi_country_cuisines = df[columns].groupby(['city', 'country']).nunique().reset_index()
    
    kpi_country_cuisines.columns = ['city', 'country', 'qtd']
    
    kpi_country_cuisines = (kpi_country_cuisines
                            .sort_values('qtd', ascending=False)
                            .reset_index(drop=True)
                            .head(10))
    fig = barplot_custom(
    df=kpi_country_cuisines,
    x='city',
    y='qtd',
    color='country',
    title='Top 10 Cities by Different Cuisines',
    top_n=10
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

def table_has_table_booking(df):
    # Agrupando e calculando a média de custo para dois por país
    columns = ['restaurant_id', 'city', 'country']
    
    df_aux = df.loc[df['has_table_booking'] == 0]
    
    kpi_city_booking = (
        df_aux[columns]
        .groupby(['city', 'country'])
        .nunique()
        .reset_index()
        .rename(columns={
            'city': 'City',
            'country': 'Country',
            'restaurant_id': 'Qty'
        })
        .sort_values('Qty', ascending=False)
        .reset_index(drop=True)
        .head(10)
    )
    
    
    styled = style_table(
        kpi_city_booking,
        col_formatadas={'Qty': '{:.0f}'},
        col_gradiente=['Qty'],
        cmap='Oranges'
    )
        
    html_table = styled.hide(axis='index').to_html()
    
    scrollable_table = f"""
    <div style="max-height: 500px; overflow-y: auto;">
        {html_table}
    
    """
    
    st.markdown('<p style="font-size:16px; font-weight:600;">Top 10 City per Number of Restaurants that Accept Reservations</p>', unsafe_allow_html=True)
    st.markdown(scrollable_table, unsafe_allow_html=True)


def table_is_delivery_now(df):
    # Agrupando e calculando a média de custo para dois por país
    columns = ['restaurant_id', 'city', 'country']
    
    df_aux = df.loc[df['is_delivering_now'] == 0]
    
    kpi_city_delivery = (
        df_aux[columns]
        .groupby(['city', 'country'])
        .nunique()
        .reset_index()
        .rename(columns={
            'city': 'City',
            'country': 'Country',
            'restaurant_id': 'Qty'
        })
        .sort_values('Qty', ascending=False)
        .reset_index(drop=True)
        .head(10)
    )
    
    
    styled = style_table(
        kpi_city_delivery,
        col_formatadas={'Qty': '{:.0f}'},
        col_gradiente=['Qty'],
        cmap='Oranges'
    )
        
    html_table = styled.hide(axis='index').to_html()
    
    scrollable_table = f"""
    <div style="max-height: 500px; overflow-y: auto;">
        {html_table}
    
    """
    
    st.markdown('<p style="font-size:16px; font-weight:600;">Top 10 City per Number of Restaurants that Accept Delivery</p>', unsafe_allow_html=True)
    st.markdown(scrollable_table, unsafe_allow_html=True)


def table_city_price_tye(df):
    kpi_city_price_tye = df.pivot_table(
    index=['country', 'city'],
    columns='price_tye',
    values='restaurant_id',
    aggfunc='count',
    fill_value=0
    )

    kpi_city_price_tye.columns.name = None
    kpi_city_price_tye = kpi_city_price_tye.reset_index()

    kpi_city_price_tye = kpi_city_price_tye.rename(columns={
    'country': 'Country',
    'city': 'City',
    })

    kpi_city_price_tye['Total'] = (
    kpi_city_price_tye['Cheap'] +
    kpi_city_price_tye['Normal'] +
    kpi_city_price_tye['Expensive'] +
    kpi_city_price_tye['Gourmet']
    )

    styled = kpi_city_price_tye.style.set_table_styles([
        {
            'selector': 'th',
            'props': [
                ('color', 'black'),
                ('background-color', '#FFE4C4'),
                ('font-size', '13px'),
                ('padding', '6px'),
                ('text-align', 'left'),
                ('border', 'none')
            ]
        },
        {
            'selector': 'td',
            'props': [
                ('font-size', '14px'),
                ('padding', '6px'),
                ('text-align', 'left'),
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
    
   
    html_table = styled.hide(axis='index').to_html()

    html_scroll = f"""
    <div style="max-height: 300px; overflow-y: auto;">
        {html_table}
    """
 

    st.markdown('<p style="font-size:16px; font-weight:600;">Number of Restaurants per Price Tier</p>', unsafe_allow_html=True)
    st.markdown(html_scroll, unsafe_allow_html=True)


    
    
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


st.header('🏙 City')

tab1, tab2 = st.tabs(["Overview Analysis", "Services Offered"])

with tab1:
    with st.container():
        fig = top_city_qtd_restaurants(df)
        st.plotly_chart(fig, use_container_width=True)
       
    with st.container():
        col1, col2 = st.columns(2, gap='large')
        with col1:
            fig = top_city_best_restaurants(df)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = top_city_worst_restaurant(df)
            st.plotly_chart(fig, use_container_width=True)

        
        
    with st.container():
        fig = top_city_cuisines(df)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        col1, col2 = st.columns(2, gap='large')
        with col1:
            table_has_table_booking(df)
        with col2:
            table_is_delivery_now(df)

    with st.container():
        table_city_price_tye(df)
 

#====================================================
#Layout Dashboard
#====================================================