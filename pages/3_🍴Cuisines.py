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

def barplot_custom(df, x, y, color, title, top_n, subtitle=None, ascend=False):
    # Ordenar e pegar os top N
    df_sorted = df.sort_values(by=y, ascending=ascend).head(top_n)

    # Define título com ou sem subtítulo
    full_title = f"<b>{title}</b>"
    if subtitle:
        full_title += f"<br><sub>{subtitle}</sub>"

    fig = px.bar(
        df_sorted,
        x=x,
        y=y,
        color_discrete_sequence=['#F08080'],
        text=y,
        labels={x: '', y: '', color: ''},
        title=full_title
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
                ('border', '0px solid transparent'),
                ('white-space', 'nowrap') 
            ]
        },
        {
            'selector': 'td',
            'props': [
                ('font-size', font_size),
                ('padding', '6px'),
                ('border', 'none'),
                ('white-space', 'nowrap')
            ]
        },
        {
            'selector': 'table',
            'props': [
                ('border-collapse', 'collapse'),
                ('border', 'none'),
                ('table-layout', 'auto'),
                ('width', '100%'),
                ('margin', '0 auto')
            ]
        }
    ], overwrite=True)

    return styled


def table_rating_votes(df, qtd):

    df = df[['restaurant_name', 'country', 'city', 'cuisines', 'price_tye', 'votes', 'aggregate_rating', 'average_cost_for_two', 'booking',  'delivery', 'type_rating']]

    kpi_restaurants = df.sort_values(by=['aggregate_rating', 'votes'], ascending=[False, False])

    kpi_restaurants = kpi_restaurants.rename(columns={
        'restaurant_name': 'Restaurant',
        'country': 'Country',
        'city': 'City',
        'cuisines': 'Cuisine',
        'votes': 'Votes',
        'aggregate_rating': 'Rating',
        'price_tye': 'Price Type',
        'average_cost_for_two': 'Cost for Two',
        'booking': 'Do Booking?',
        'delivery': 'Do Delivery?',
        'type_rating': 'Type Rating'
        
    }).head(qtd)

    styled_df = style_table(
    df=kpi_restaurants,
    col_formatadas={
            'Rating': '{:.2f}',
            'Cost for Two': '{:.2f}'
        },
    cmap='Oranges'
    )

    # Converte para HTML ocultando índice
    html_table = styled_df.hide(axis='index').to_html()


    st.markdown('<p style="font-size:16px; font-weight:bold;">Top '+str(qtd)+' Restaurants</p>', unsafe_allow_html=True)
    # Exibir com scroll
    st.markdown(f"""
        <div style="max-height: 410px; overflow-y: auto;">
            {html_table}

    """, unsafe_allow_html=True)

def top_best_cuisines(df, qtd):
    columns = ['aggregate_rating', 'cuisines']

    kpi_best_cuisines = df[columns].sort_values(by='aggregate_rating', ascending=False)
    
    kpi_best_cuisines = ( kpi_best_cuisines
        .groupby('cuisines')
        .first()
        .reset_index()
    ).head(10)
    
    kpi_best_cuisines.sort_values(by='aggregate_rating', ascending=False)

    fig = barplot_custom(
    df=kpi_best_cuisines,
    x='cuisines',
    y='aggregate_rating',
    color='cuisines',
    title='Top ' +str(qtd)+ '  Best Cuisines',
    top_n=qtd,
    ascend=False
    )
        
    return fig


def top_worst_cuisines(df, qtd):
    columns = ['aggregate_rating', 'cuisines']

    kpi_worst_cuisines = df[columns].sort_values(by='aggregate_rating', ascending=True)
    
    kpi_worst_cuisines = ( kpi_worst_cuisines
        .groupby('cuisines')
        .first()
        .reset_index()
    ).head(10)
    
    kpi_worst_cuisines.sort_values(by='aggregate_rating', ascending=True)

    fig = barplot_custom(
    df=kpi_worst_cuisines,
    x='cuisines',
    y='aggregate_rating',
    color='cuisines',
    title='Top 10 '+ str(qtd)+' Worst Cuisines',
    top_n=qtd,
    ascend=True
    )
        
    return fig

def best_restaurants_cuisine(df):
    '''
    1. Dos restaurantes que possuem o tipo de culinária italiana, qual o nome do restaurante com a maior média de avaliação?
    3. Dos restaurantes que possuem o tipo de culinária americana, qual o nome do restaurante com a maior média de avaliação?
    5. Dos restaurantes que possuem o tipo de culinária árabe, qual o nome do restaurante com a maior média de avaliação?
    7. Dos restaurantes que possuem o tipo de culinária japonesa, qual o nome do restaurante com a maior média de avaliação?
    9. Dos restaurantes que possuem o tipo de culinária caseira, qual o nome do restaurante com a maior média de avaliação?
    '''
    
    columns = ['restaurant_id', 'restaurant_name', 'aggregate_rating', 'cuisines']
    
    cuisines = ['Italian', 'American', 'Arabian', 'Japanese', 'Home-made']
    
    df_aux = df[df['cuisines'].isin(cuisines)]
    
    kpi_best_restaurant_cuisine = df_aux[columns].sort_values(
        by=['cuisines', 'aggregate_rating', 'restaurant_id'],
        ascending=[True, False, True]
    )
    
    kpi_best_restaurant_cuisine = ( kpi_best_restaurant_cuisine
        .groupby('cuisines')
        .first()
        .reset_index()
    )
    
    return kpi_best_restaurant_cuisine

        



#====================================================
#Barra Lateral
#====================================================

image_path = os.path.join('images', 'logo.png')


image_path = os.path.join('images', 'logo.png')
image_base64 = base64.b64encode(open(image_path, "rb").read()).decode()

st.sidebar.markdown(f"""
    <div style="display: flex; align-items: center;">
        <img src="data:image/png;base64,{image_base64}" width="30" style="margin-right: 10px;" />
        <h1 style="font-size: 20px; margin: 0;">Fome Zero</h1>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""Please choise filter""")

st.sidebar.markdown(
    """
    <style>
    div[data-baseweb="select"] > div {
        max-height: 180px;
        overflow-y: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

qt_restaurantes = st.sidebar.slider(
    'Select the number of top restaurants per cuisine',
    min_value=1, max_value=20, value=10
)

country_options = st.sidebar.multiselect(
    "Select Countries",
    list(df['country'].unique()),
    default=['Brazil', 'England', 'United States of America']
)

cuisines_options = st.sidebar.multiselect(
    "Select Cuisines",
    list(df['cuisines'].unique()),
    default=list(df['cuisines'].unique())
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

linhas_selecionadas = df['cuisines'].isin( cuisines_options )
df = df.loc[linhas_selecionadas,:]

linhas_selecionadas = df['price_tye'].isin( price_options )
df = df.loc[linhas_selecionadas,:]

linhas_selecionadas = df['type_rating'].isin( rating_options )
df = df.loc[linhas_selecionadas,:]

linhas_selecionadas = df['delivery'].isin( delivery_options )
df = df.loc[linhas_selecionadas,:]

linhas_selecionadas = df['booking'].isin( booking_options )
df = df.loc[linhas_selecionadas,:]



st.header('🍴 Cuisines')
st.markdown('<hr style="border:0.2px solid #F5F5F5; margin: 15px 0;">', unsafe_allow_html=True)

#====================================================
#Layout Dashboard
#====================================================

with st.container():
    st.markdown('<p style="font-size:16px; font-weight:bold;">Best Restaurants by Main Cuisines</p>', unsafe_allow_html=True)

    cards = best_restaurants_cuisine(df)

    cols = st.columns(len(cards))
    for i, row in enumerate(cards.itertuples()):
        with cols[i]:
            st.markdown(f"""
                <div style="background-color:#FFE4C4; padding:16px; border-radius:8px; box-shadow:0px 0px 6px rgba(0,0,0,0.1); margin-bottom: 30px;">
                    <p style="margin-bottom:8px; font-size:14px">🍴{row.cuisines}</p>
                    <p style="font-size:12px">{row.restaurant_name}</p>
                    <h4>{row.aggregate_rating:.1f}<strong>/5.0</strong></h4>
                </div>
            """, unsafe_allow_html=True)

with st.container():
    table_rating_votes(df, qt_restaurantes)

with st.container():
    col1, col2 = st.columns(2, gap='large')
    with col1:
        fig = top_best_cuisines(df, qt_restaurantes)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = top_worst_cuisines(df, qt_restaurantes)
        st.plotly_chart(fig, use_container_width=True)



