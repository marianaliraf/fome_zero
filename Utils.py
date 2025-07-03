import pandas as pd
from datetime import datetime
import os
import inflection

class Utils:
    COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
    }
    
    COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
    }
    
    def __init__(self):
        pass

    def read_dataset(self, caminho):
        dataset = pd.read_csv(caminho)
        return dataset

    
    def country_name(self, country_id):
      return self.COUNTRIES[country_id]

    def color_name(self, color_code):
      return self.COLORS[color_code]

    def create_price_tye(self, price_range):
      if price_range == 1:
        return "Cheap"
      elif price_range == 2:
        return "Normal"
      elif price_range == 3:
        return "Expensive"
      else:
        return "Gourmet"

    def rename_columns(self, dataframe):
      df = dataframe.copy()
      title = lambda x: inflection.titleize(x)
      snakecase = lambda x: inflection.underscore(x)
      spaces = lambda x: x.replace(" ", "")
      cols_old = list(df.columns)
      cols_old = list(map(title, cols_old))
      cols_old = list(map(spaces, cols_old))
      cols_new = list(map(snakecase, cols_old))
      df.columns = cols_new
      return df

    def create_rating_type(self, df):
        rating_color_map = {
            'darkgreen': 'Excellent',
            'darkred': 'Poor or Not rated',
            'orange': 'Average',
            'red': 'Average',
            'green': 'Very Good',
            'lightgreen': 'Good'
        }
        
        df['type_rating'] = df['rating_color'].map(rating_color_map)
        return df
        
    
    def clean_dataset(self, df):
        #Tratamento dos Dados
        df = df.dropna()

        df = self.rename_columns(df)
        
        df['rating_color'] =  df['rating_color'].map(lambda color: self.color_name(color))
        
        df['country'] =  df['country_code'].map(lambda country: self.country_name(country))
        
        df['price_tye'] =  df['price_range'].map(lambda price: self.create_price_tye(price))
        
        df["cuisines"] = df["cuisines"].map(lambda x: x.split(",")[0])

        df['booking'] = df['has_table_booking'].map({0: 'Yes', 1: 'No'})

        df['delivery'] = df['is_delivering_now'].map({0: 'Yes', 1: 'No'})

        df = df.drop_duplicates()  

        df = self.create_rating_type(df)
        
        return df


        