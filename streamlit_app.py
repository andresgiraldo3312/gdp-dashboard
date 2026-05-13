import streamlit as st
import pandas as pd
import math
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import yfinance as yf

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Dashboard Bolsa Colombia',
    page_icon=':chart_with_upwards_trend:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_stock_data(ticker, period='1y'):
    """Grab stock data from Yahoo Finance.

    This uses caching to avoid having to fetch the data every time.
    """
    data = yf.download(ticker, period=period)
    data.reset_index(inplace=True)
    return data

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :chart_with_upwards_trend: Dashboard Bolsa de Valores de Colombia

Visualiza datos históricos de acciones de la Bolsa de Valores de Colombia (BVC). Incluye acciones como Celsia, ISA, GEB y más.
'''

# Add some spacing
''
''

period = st.selectbox(
    'Selecciona el período:',
    ['1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'max'],
    index=3  # Default to 1y
)

stocks = ['CELSIA.CO', 'ISA.CO', 'GEB.CO', 'ECOPETROL.CO', 'BANCOLOMBIA.CO']

selected_stocks = st.multiselect(
    'Selecciona las acciones que deseas ver:',
    stocks,
    ['CELSIA.CO', 'ISA.CO', 'GEB.CO'])

''
''
''

# Filter the data
if selected_stocks:
    stock_data = {}
    for stock in selected_stocks:
        data = get_stock_data(stock, period)
        if not data.empty:
            data['Ticker'] = stock
            stock_data[stock] = data
    
    if stock_data:
        # Combine all data
        combined_df = pd.concat(stock_data.values())
        
        st.header('Precios de Acciones a lo Largo del Tiempo', divider='gray')
        
        ''
        
        st.line_chart(
            combined_df,
            x='Date',
            y='Close',
            color='Ticker',
        )
        
        ''
        ''
        
        st.header('Regresión Lineal para Acciones', divider='gray')
        
        ''
        
        if selected_stocks:
            stock = selected_stocks[0]  # Usar la primera acción seleccionada
            if stock in stock_data:
                data = stock_data[stock].dropna()
                
                if len(data) > 1:
                    # Usar el índice como X (días)
                    data['Days'] = (data['Date'] - data['Date'].min()).dt.days
                    X = data[['Days']]
                    y = data['Close']
                    
                    model = LinearRegression()
                    model.fit(X, y)
                    
                    y_pred = model.predict(X)
                    r2 = r2_score(y, y_pred)
                    
                    st.write(f"**Acción:** {stock}")
                    st.write(f"**Coeficiente (pendiente):** {model.coef_[0]:.2f}")
                    st.write(f"**Intercepto:** {model.intercept_:.2f}")
                    st.write(f"**R²:** {r2:.4f}")
                    
                    # Predicción para el próximo día
                    next_day = data['Days'].max() + 1
                    pred_price = model.predict([[next_day]])[0]
                    st.write(f"**Predicción precio para mañana:** {pred_price:.2f}")
                else:
                    st.write("No hay suficientes datos para realizar la regresión.")
            else:
                st.write("No hay datos para la acción seleccionada.")
        else:
            st.write("Selecciona al menos una acción.")
    else:
        st.warning("No se pudieron obtener datos para las acciones seleccionadas.")
else:
    st.warning("Selecciona al menos una acción.")
