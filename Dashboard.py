import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta
import time

# Configuration de la page
st.set_page_config(
    page_title="Stock Tracker - yfinance",
    page_icon="📈",
    layout="wide"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .stock-price {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .stock-change-positive {
        color: #00cc96;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .stock-change-negative {
        color: #ef553b;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Titre principal
st.title("📈 Suivi Boursier en Temps Réel avec yfinance")

# Sidebar pour les contrôles
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Liste des symboles prédéfinis
    default_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    
    # Sélection du symbole
    symbol = st.selectbox(
        "Choisir un symbole",
        options=default_symbols + ["Autre..."],
        index=0
    )
    
    if symbol == "Autre...":
        symbol = st.text_input("Entrer un symbole", value="AAPL").upper()
    
    # Période d'affichage
    period = st.selectbox(
        "Période",
        options=["1d", "5d", "1mo", "3mo", "6mo", "1y"],
        index=0
    )
    
    # Intervalle
    interval_map = {
        "1m": "1 minute",
        "2m": "2 minutes",
        "5m": "5 minutes",
        "15m": "15 minutes",
        "30m": "30 minutes",
        "1h": "1 heure",
        "1d": "1 jour"
    }
    
    interval = st.selectbox(
        "Intervalle",
        options=list(interval_map.keys()),
        format_func=lambda x: interval_map[x],
        index=0 if period == "1d" else 4
    )
    
    # Auto-refresh
    auto_refresh = st.checkbox("Actualisation automatique", value=True)
    refresh_rate = st.slider(
        "Fréquence d'actualisation (secondes)",
        min_value=5,
        max_value=60,
        value=10,
        step=5,
        disabled=not auto_refresh
    )
    
    st.markdown("---")
    
    # Informations
    st.info(
        "📊 Données fournies par yfinance\n\n"
        "⏱️ Données en temps réel (avec un délai de 15 minutes pour certaines bourses)"
    )

# Fonction pour charger les données
@st.cache_data(ttl=refresh_rate if auto_refresh else 300)
def load_stock_data(symbol, period, interval):
    """Charge les données boursières avec cache"""
    try:
        ticker = yf.Ticker(symbol)
        
        # Données historiques
        hist = ticker.history(period=period, interval=interval)
        
        # Informations en temps réel
        info = ticker.info
        
        return hist, info
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return None, None

# Chargement des données
hist, info = load_stock_data(symbol, period, interval)

if hist is not None and not hist.empty:
    
    # Layout en colonnes
    col1, col2, col3, col4 = st.columns(4)
    
    # Prix actuel
    current_price = hist['Close'].iloc[-1]
    previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
    change = current_price - previous_close
    change_pct = (change / previous_close) * 100
    
    with col1:
        st.metric(
            label=f"{symbol} - Prix actuel",
            value=f"${current_price:.2f}",
            delta=f"{change:.2f} ({change_pct:.2f}%)"
        )
    
    # Plus haut du jour
    with col2:
        day_high = hist['High'].iloc[-1]
        st.metric(
            label="Plus haut du jour",
            value=f"${day_high:.2f}",
            delta=None
        )
    
    # Plus bas du jour
    with col3:
        day_low = hist['Low'].iloc[-1]
        st.metric(
            label="Plus bas du jour",
            value=f"${day_low:.2f}",
            delta=None
        )
    
    # Volume
    with col4:
        volume = hist['Volume'].iloc[-1]
        volume_formatted = f"{volume/1e6:.1f}M" if volume > 1e6 else f"{volume/1e3:.1f}K"
        st.metric(
            label="Volume",
            value=volume_formatted,
            delta=None
        )
    
    # Graphique principal
    st.subheader(f"📉 Évolution du prix - {symbol}")
    
    fig = go.Figure()
    
    # Ajouter les prix (chandeliers ou ligne)
    if interval in ["1m", "2m", "5m", "15m", "30m", "1h"]:
        # Graphique en chandeliers pour les intervalles courts
        fig.add_trace(go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name='Prix'
        ))
    else:
        # Graphique en ligne pour les intervalles longs
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=hist['Close'],
            mode='lines',
            name='Prix',
            line=dict(color='#1f77b4', width=2)
        ))
    
    # Ajouter le volume
    fig.add_trace(go.Bar(
        x=hist.index,
        y=hist['Volume'],
        name='Volume',
        yaxis='y2',
        marker=dict(color='lightgray', opacity=0.3)
    ))
    
    # Configuration du layout
    fig.update_layout(
        title=f"{symbol} - {period}",
        yaxis_title="Prix ($)",
        yaxis2=dict(
            title="Volume",
            overlaying='y',
            side='right',
            showgrid=False
        ),
        xaxis_title="Date",
        height=600,
        hovermode='x unified',
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Informations supplémentaires
    with st.expander("📊 Plus de détails"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Informations sur l'entreprise")
            if info:
                st.write(f"**Nom :** {info.get('longName', 'N/A')}")
                st.write(f"**Secteur :** {info.get('sector', 'N/A')}")
                st.write(f"**Industrie :** {info.get('industry', 'N/A')}")
                st.write(f"**Site web :** {info.get('website', 'N/A')}")
        
        with col2:
            st.subheader("Statistiques")
            if info:
                st.write(f"**Capitalisation :** ${info.get('marketCap', 0):,.0f}")
                st.write(f"**P/E :** {info.get('trailingPE', 'N/A')}")
                st.write(f"**Dividende :** {info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "**Dividende :** N/A")
                st.write(f"**Beta :** {info.get('beta', 'N/A')}")
    
    # Données tabulaires
    with st.expander("📋 Données historiques"):
        st.dataframe(
            hist[['Open', 'High', 'Low', 'Close', 'Volume']].tail(20).style.format({
                'Open': '${:.2f}',
                'High': '${:.2f}',
                'Low': '${:.2f}',
                'Close': '${:.2f}',
                'Volume': '{:,.0f}'
            }),
            use_container_width=True
        )
    
    # Indicateurs techniques
    with st.expander("📈 Indicateurs techniques"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Moyennes mobiles
            ma_20 = hist['Close'].rolling(window=20).mean()
            ma_50 = hist['Close'].rolling(window=50).mean()
            
            st.subheader("Moyennes mobiles")
            st.write(f"**MA(20) :** ${ma_20.iloc[-1]:.2f}")
            st.write(f"**MA(50) :** ${ma_50.iloc[-1]:.2f}")
        
        with col2:
            # RSI
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            st.subheader("RSI (14)")
            current_rsi = rsi.iloc[-1]
            st.write(f"**RSI :** {current_rsi:.2f}")
            if current_rsi > 70:
                st.warning("⚠️ Surachat (RSI > 70)")
            elif current_rsi < 30:
                st.success("💚 Survente (RSI < 30)")
    
    # Dernière mise à jour
    st.caption(f"Dernière mise à jour : {datetime.now().strftime('%H:%M:%S')}")
    
    # Actualisation automatique
    if auto_refresh:
        time.sleep(1)
        st.rerun()

else:
    st.warning(f"Aucune donnée disponible pour {symbol}")

# Section multi-symboles
st.markdown("---")
st.header("📊 Comparaison multiple")

# Sélection des symboles à comparer
compare_symbols = st.multiselect(
    "Choisir les symboles à comparer",
    options=default_symbols + [symbol] if symbol not in default_symbols else default_symbols,
    default=[symbol] if symbol else []
)

if compare_symbols:
    # Charger les données pour chaque symbole
    compare_data = {}
    for sym in compare_symbols:
        ticker = yf.Ticker(sym)
        hist_comp = ticker.history(period="5d", interval="15m")
        if not hist_comp.empty:
            compare_data[sym] = hist_comp['Close']
    
    if compare_data:
        # Créer un DataFrame avec tous les prix
        df_compare = pd.DataFrame(compare_data)
        df_compare = df_compare.fillna(method='ffill')
        
        # Normaliser pour comparaison (base 100)
        df_normalized = (df_compare / df_compare.iloc[0]) * 100
        
        # Graphique comparatif
        fig_compare = go.Figure()
        for col in df_normalized.columns:
            fig_compare.add_trace(go.Scatter(
                x=df_normalized.index,
                y=df_normalized[col],
                mode='lines',
                name=col
            ))
        
        fig_compare.update_layout(
            title="Performance comparée (base 100)",
            xaxis_title="Date",
            yaxis_title="Performance (%)",
            height=400,
            hovermode='x unified',
            template='plotly_white'
        )
        
        st.plotly_chart(fig_compare, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>"
    "Données fournies par yfinance | ⚠️ Les données en temps réel peuvent avoir un délai"
    "</p>",
    unsafe_allow_html=True
)
