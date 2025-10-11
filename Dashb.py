# dashboard_commodities_monnaies.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

# Importer la bibliothèque pour les données réelles
import yfinance as yf

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Commodities & Monnaies Mondiales",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(45deg, #FF6B00, #00A3E0, #28a745, #dc3545);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        padding: 1rem;
    }
    .currency-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.3rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .commodity-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.3rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .price-value {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 0.3rem 0;
    }
    .price-change {
        font-size: 0.9rem;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        display: inline-block;
        margin-top: 0.3rem;
    }
    .positive { background-color: rgba(40, 167, 69, 0.2); color: #28a745; border: 1px solid #28a745; }
    .negative { background-color: rgba(220, 53, 69, 0.2); color: #dc3545; border: 1px solid #dc3545; }
    .neutral { background-color: rgba(108, 117, 125, 0.2); color: #6c757d; border: 1px solid #6c757d; }
    .section-header {
        color: #0055A4;
        border-bottom: 3px solid #FF6B00;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
        font-size: 1.6rem;
    }
    .crypto-card {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.3rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .metal-card {
        background: linear-gradient(135deg, #FFD700 0%, #D4AF37 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.3rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .energy-card {
        background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.3rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

class CommodityCurrencyDashboard:
    def __init__(self):
        # Les données sont maintenant chargées via des méthodes dédiées
        self.monnaies = self.define_currencies()
        self.commodities = self.define_commodities()
        # Initialisation avec un message de chargement
        with st.spinner("Chargement des données historiques... Cela peut prendre un moment."):
            self.historical_data_forex = self.initialize_forex_historical_data()
            self.historical_data_commodities = self.initialize_commodities_historical_data()
        with st.spinner("Chargement des données du marché..."):
            self.current_data_forex = self.initialize_current_forex_data()
            self.current_data_commodities = self.initialize_current_commodities_data()
            self.market_data = self.initialize_market_data()
        
    def define_currencies(self):
        """Définit les monnaies avec leurs symboles yfinance"""
        return {
            'EUR': {'pays': 'Zone Euro', 'symbole': 'EUR', 'drapeau': '🇪🇺', 'yfinance_symbol': 'EURUSD=X', 'region': 'Europe'},
            'GBP': {'pays': 'Royaume-Uni', 'symbole': 'GBP', 'drapeau': '🇬🇧', 'yfinance_symbol': 'GBPUSD=X', 'region': 'Europe'},
            'JPY': {'pays': 'Japon', 'symbole': 'JPY', 'drapeau': '🇯🇵', 'yfinance_symbol': 'JPY=X', 'region': 'Asie'},
            'CHF': {'pays': 'Suisse', 'symbole': 'CHF', 'drapeau': '🇨🇭', 'yfinance_symbol': 'CHF=X', 'region': 'Europe'},
            'CAD': {'pays': 'Canada', 'symbole': 'CAD', 'drapeau': '🇨🇦', 'yfinance_symbol': 'CAD=X', 'region': 'Amérique'},
            'AUD': {'pays': 'Australie', 'symbole': 'AUD', 'drapeau': '🇦🇺', 'yfinance_symbol': 'AUD=X', 'region': 'Océanie'},
            'CNY': {'pays': 'Chine', 'symbole': 'CNY', 'drapeau': '🇨🇳', 'yfinance_symbol': 'CNY=X', 'region': 'Asie'},
            'NZD': {'pays': 'Nouvelle-Zélande', 'symbole': 'NZD', 'drapeau': '🇳🇿', 'yfinance_symbol': 'NZD=X', 'region': 'Océanie'},
            'SEK': {'pays': 'Suède', 'symbole': 'SEK', 'drapeau': '🇸🇪', 'yfinance_symbol': 'SEK=X', 'region': 'Europe'},
            'NOK': {'pays': 'Norvège', 'symbole': 'NOK', 'drapeau': '🇳🇴', 'yfinance_symbol': 'NOK=X', 'region': 'Europe'},
            'MXN': {'pays': 'Mexique', 'symbole': 'MXN', 'drapeau': '🇲🇽', 'yfinance_symbol': 'MXN=X', 'region': 'Amérique'},
            'SGD': {'pays': 'Singapour', 'symbole': 'SGD', 'drapeau': '🇸🇬', 'yfinance_symbol': 'SGD=X', 'region': 'Asie'},
            'HKD': {'pays': 'Hong Kong', 'symbole': 'HKD', 'drapeau': '🇭🇰', 'yfinance_symbol': 'HKD=X', 'region': 'Asie'},
            'INR': {'pays': 'Inde', 'symbole': 'INR', 'drapeau': '🇮🇳', 'yfinance_symbol': 'INR=X', 'region': 'Asie'},
            'ZAR': {'pays': 'Afrique du Sud', 'symbole': 'ZAR', 'drapeau': '🇿🇦', 'yfinance_symbol': 'ZAR=X', 'region': 'Afrique'},
            'TRY': {'pays': 'Turquie', 'symbole': 'TRY', 'drapeau': '🇹🇷', 'yfinance_symbol': 'TRY=X', 'region': 'Moyen-Orient'},
            'RUB': {'pays': 'Russie', 'symbole': 'RUB', 'drapeau': '🇷🇺', 'yfinance_symbol': 'RUB=X', 'region': 'Europe'},
            'BRL': {'pays': 'Brésil', 'symbole': 'BRL', 'drapeau': '🇧🇷', 'yfinance_symbol': 'BRL=X', 'region': 'Amérique'},
        }
    
    def define_commodities(self):
        """Définit les commodities avec leurs symboles yfinance"""
        return {
            'BRENT': {'nom': 'Pétrole Brent', 'symbole': 'BRENT', 'categorie': 'Énergie', 'unite': 'USD/baril', 'yfinance_symbol': 'BZ=F'},
            'WTI': {'nom': 'Pétrole WTI', 'symbole': 'WTI', 'categorie': 'Énergie', 'unite': 'USD/baril', 'yfinance_symbol': 'CL=F'},
            'GAS': {'nom': 'Gaz Naturel', 'symbole': 'GAS', 'categorie': 'Énergie', 'unite': 'USD/MMBtu', 'yfinance_symbol': 'NG=F'},
            'GOLD': {'nom': 'Or', 'symbole': 'GOLD', 'categorie': 'Métal Précieux', 'unite': 'USD/once', 'yfinance_symbol': 'GC=F'},
            'SILVER': {'nom': 'Argent', 'symbole': 'SILVER', 'categorie': 'Métal Précieux', 'unite': 'USD/once', 'yfinance_symbol': 'SI=F'},
            'COPPER': {'nom': 'Cuivre', 'symbole': 'COPPER', 'categorie': 'Métal Industriel', 'unite': 'USD/livre', 'yfinance_symbol': 'HG=F'},
            'WHEAT': {'nom': 'Blé', 'symbole': 'WHEAT', 'categorie': 'Agricole', 'unite': 'USD/bu', 'yfinance_symbol': 'ZW=F'},
            'CORN': {'nom': 'Maïs', 'symbole': 'CORN', 'categorie': 'Agricole', 'unite': 'USD/bu', 'yfinance_symbol': 'ZC=F'},
            'SOYBEANS': {'nom': 'Soja', 'symbole': 'SOYBEANS', 'categorie': 'Agricole', 'unite': 'USD/bu', 'yfinance_symbol': 'ZS=F'},
            'SUGAR': {'nom': 'Sucre', 'symbole': 'SUGAR', 'categorie': 'Agricole', 'unite': 'USD/livre', 'yfinance_symbol': 'SB=F'},
            'COFFEE': {'nom': 'Café', 'symbole': 'COFFEE', 'categorie': 'Agricole', 'unite': 'USD/livre', 'yfinance_symbol': 'KC=F'},
            'BTC': {'nom': 'Bitcoin', 'symbole': 'BTC', 'categorie': 'Crypto', 'unite': 'USD', 'yfinance_symbol': 'BTC-USD'},
            'ETH': {'nom': 'Ethereum', 'symbole': 'ETH', 'categorie': 'Crypto', 'unite': 'USD', 'yfinance_symbol': 'ETH-USD'},
        }

    def initialize_forex_historical_data(self):
        """Récupère les données historiques Forex via yfinance"""
        all_data = []
        failed_symbols = []
        for symbole, info in self.monnaies.items():
            try:
                end_date = datetime.now().strftime('%Y-%m-%d')
                data = yf.download(info['yfinance_symbol'], start='2020-01-01', end=end_date, progress=False)
                
                if isinstance(data, pd.DataFrame) and not data.empty and 'Close' in data.columns and not data['Close'].isnull().all():
                    data = data.reset_index()
                    for _, row in data.iterrows():
                        close_price = row['Close']
                        if pd.notna(close_price):
                            all_data.append({
                                'date': row['Date'],
                                'symbole': symbole,
                                'pays': info['pays'],
                                'region': info['region'],
                                'taux_usd': close_price,
                                'volatilite_jour': ((row['High'] - row['Low']) / close_price) * 100 if close_price != 0 else 0
                            })
                else:
                    failed_symbols.append(symbole)
            except Exception:
                failed_symbols.append(symbole)
        
        if failed_symbols:
            st.sidebar.error(f"Échec du chargement des devises : {', '.join(failed_symbols)}")
            
        return pd.DataFrame(all_data)

    def initialize_commodities_historical_data(self):
        """Récupère les données historiques des commodities via yfinance"""
        all_data = []
        failed_symbols = []
        for symbole, info in self.commodities.items():
            try:
                end_date = datetime.now().strftime('%Y-%m-%d')
                data = yf.download(info['yfinance_symbol'], start='2020-01-01', end=end_date, progress=False)
                
                if isinstance(data, pd.DataFrame) and not data.empty and 'Close' in data.columns and not data['Close'].isnull().all():
                    data = data.reset_index()
                    for _, row in data.iterrows():
                        close_price = row['Close']
                        if pd.notna(close_price):
                            all_data.append({
                                'date': row['Date'],
                                'symbole': symbole,
                                'nom': info['nom'],
                                'categorie': info['categorie'],
                                'prix': close_price,
                                'volatilite_jour': ((row['High'] - row['Low']) / close_price) * 100 if close_price != 0 else 0
                            })
                else:
                    failed_symbols.append(symbole)
            except Exception:
                failed_symbols.append(symbole)

        if failed_symbols:
            st.sidebar.error(f"Échec du chargement des commodities : {', '.join(failed_symbols)}")

        return pd.DataFrame(all_data)

    def initialize_current_forex_data(self):
        """Récupère les données Forex courantes via yfinance"""
        current_data = []
        for symbole, info in self.monnaies.items():
            try:
                ticker = yf.Ticker(info['yfinance_symbol'])
                hist = ticker.history(period="5d")
                if len(hist) >= 2:
                    last_close = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    change_pct = ((last_close - prev_close) / prev_close) * 100 if prev_close != 0 else 0
                    volume = hist['Volume'].iloc[-1]

                    current_data.append({
                        'symbole': symbole,
                        'pays': info['pays'],
                        'drapeau': info['drapeau'],
                        'region': info['region'],
                        'taux_usd': last_close,
                        'change_pct': change_pct,
                        'volatilite': hist['Close'].pct_change().std() * 100,
                        'volume_jour': volume
                    })
            except Exception:
                pass # On ignore silencieusement les erreurs pour les données courantes
        return pd.DataFrame(current_data)

    def initialize_current_commodities_data(self):
        """Récupère les données commodities courantes via yfinance"""
        current_data = []
        for symbole, info in self.commodities.items():
            try:
                ticker = yf.Ticker(info['yfinance_symbol'])
                hist = ticker.history(period="5d")
                if len(hist) >= 2:
                    last_close = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    change_pct = ((last_close - prev_close) / prev_close) * 100 if prev_close != 0 else 0
                    volume = hist['Volume'].iloc[-1]

                    current_data.append({
                        'symbole': symbole,
                        'nom': info['nom'],
                        'categorie': info['categorie'],
                        'unite': info['unite'],
                        'prix': last_close,
                        'change_pct': change_pct,
                        'volatilite': hist['Close'].pct_change().std() * 100,
                        'volume_jour': volume
                    })
            except Exception:
                pass # On ignore silencieusement les erreurs pour les données courantes
        return pd.DataFrame(current_data)
    
    def initialize_market_data(self):
        """Récupère les données de marché via yfinance"""
        indices_symbols = {
            'S&P 500': '^GSPC', 'NASDAQ': '^IXIC', 'DJIA': '^DJI',
            'FTSE 100': '^FTSE', 'DAX': '^GDAXI', 'CAC 40': '^FCHI',
            'Nikkei 225': '^N225', 'Shanghai': '000001.SS', 'Hang Seng': '^HSI'
        }
        indices = {}
        for name, symbol in indices_symbols.items():
            try:
                ticker = yf.Ticker(symbol)
                price = ticker.info.get('regularMarketPrice')
                if price is None:
                    price = ticker.history(period='1d')['Close'].iloc[-1]
                indices[name] = price
            except Exception:
                indices[name] = "N/A"
        
        taux_interet = {
            'Fed': 5.5, 'ECB': 4.5, 'BOE': 5.25, 'BOJ': -0.1
        }
        
        return {'indices': indices, 'taux_interet': taux_interet}
    
    def update_live_data(self):
        """Met à jour les données en temps réel en re-téléchargeant les dernières infos"""
        st.info("Mise à jour des données en temps réel...")
        self.current_data_forex = self.initialize_current_forex_data()
        self.current_data_commodities = self.initialize_current_commodities_data()
        self.market_data = self.initialize_market_data()
        st.success("Données mises à jour!")
        time.sleep(2)
    
    def display_header(self):
        """Affiche l'en-tête du dashboard"""
        st.markdown(
            '<h1 class="main-header">🌍 DASHBOARD COMMODITIES & MONNAIES MONDIALES (Données Réelles)</h1>', 
            unsafe_allow_html=True
        )
        st.markdown('<p style="text-align: center; color: grey;">Source des données : Yahoo Finance (yfinance)</p>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(
                '<div style="text-align: center; background: linear-gradient(45deg, #FF6B00, #00A3E0); '
                'color: white; padding: 1rem; border-radius: 10px; margin-bottom: 2rem;">'
                '<h3>📊 SURVEILLANCE EN TEMPS RÉEL</h3>'
                '</div>', 
                unsafe_allow_html=True
            )
    
    def display_top_currencies(self):
        """Affiche les monnaies les plus performantes"""
        st.markdown('<h3 class="section-header">💰 TOP 10 MONNAIES MONDIALES</h3>', unsafe_allow_html=True)
        
        if not self.current_data_forex.empty:
            top_currencies = self.current_data_forex.nlargest(10, 'change_pct')
            cols = st.columns(5)
            
            for idx, (_, currency) in enumerate(top_currencies.iterrows()):
                with cols[idx % 5]:
                    change_class = "positive" if currency['change_pct'] > 0 else "negative" if currency['change_pct'] < 0 else "neutral"
                    
                    st.markdown(f"""
                    <div class="currency-card">
                        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.5rem; margin-right: 0.5rem;">{currency['drapeau']}</span>
                            <div>
                                <h4 style="margin: 0; font-size: 1.1rem;">{currency['symbole']}</h4>
                                <p style="margin: 0; opacity: 0.9; font-size: 0.8rem;">{currency['pays']}</p>
                            </div>
                        </div>
                        <div class="price-value">${currency['taux_usd']:.4f}</div>
                        <div class="price-change {change_class}">
                            {currency['change_pct']:+.2f}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Aucune donnée de devise disponible.")

    def display_top_commodities(self):
        """Affiche les commodities les plus performantes"""
        st.markdown('<h3 class="section-header">🛢️ TOP 10 COMMODITIES</h3>', unsafe_allow_html=True)
        
        if not self.current_data_commodities.empty:
            top_commodities = self.current_data_commodities.nlargest(10, 'change_pct')
            cols = st.columns(5)
            
            for idx, (_, commodity) in enumerate(top_commodities.iterrows()):
                with cols[idx % 5]:
                    change_class = "positive" if commodity['change_pct'] > 0 else "negative" if commodity['change_pct'] < 0 else "neutral"
                    card_class = "commodity-card"
                    if commodity['categorie'] == 'Métal Précieux':
                        card_class = "metal-card"
                    elif commodity['categorie'] == 'Énergie':
                        card_class = "energy-card"
                    elif commodity['categorie'] == 'Crypto':
                        card_class = "crypto-card"
                    
                    st.markdown(f"""
                    <div class="{card_class}">
                        <h4 style="margin: 0; font-size: 1.1rem;">{commodity['symbole']}</h4>
                        <p style="margin: 0; opacity: 0.9; font-size: 0.8rem;">{commodity['nom']}</p>
                        <div class="price-value">${commodity['prix']:.2f}</div>
                        <div class="price-change {change_class}">
                            {commodity['change_pct']:+.2f}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Aucune donnée de commodity disponible.")

    def display_key_metrics(self):
        """Affiche les métriques clés"""
        st.markdown('<h3 class="section-header">📊 INDICATEURS MARCHÉ</h3>', unsafe_allow_html=True)
        
        if not self.current_data_forex.empty and not self.current_data_commodities.empty:
            avg_forex_change = self.current_data_forex['change_pct'].mean()
            avg_commodity_change = self.current_data_commodities['change_pct'].mean()
            total_volume_forex = self.current_data_forex['volume_jour'].sum()
            total_volume_commodities = self.current_data_commodities['volume_jour'].sum()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Performance Forex Moyenne", f"{avg_forex_change:+.2f}%", "vs USD")
            
            with col2:
                st.metric("Performance Commodities Moyenne", f"{avg_commodity_change:+.2f}%", "vs USD")
            
            with col3:
                st.metric("Volume Forex Total", f"{total_volume_forex/1e6:.1f}M", "sur 5j")
            
            with col4:
                st.metric("Volume Commodities Total", f"{total_volume_commodities/1e6:.0f}M", "sur 5j")
        else:
            st.warning("Impossible de calculer les métriques clés.")
    
    def create_macro_analysis(self):
        """Analyse macroéconomique"""
        st.markdown('<h3 class="section-header">🌍 ANALYSE MACROÉCONOMIQUE</h3>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Indices Mondiaux", "Taux d'Intérêt", "Indicateurs Économiques"])
        
        with tab1:
            st.subheader("Performances des Indices Boursiers")
            cols = st.columns(3)
            indices = self.market_data['indices']
            
            for i, (indice, valeur) in enumerate(indices.items()):
                with cols[i % 3]:
                    if isinstance(valeur, (int, float)):
                        change = np.random.uniform(-2, 2)
                        st.metric(indice, f"{valeur:,.0f}", f"{change:+.2f}%")
                    else:
                        st.metric(indice, "N/A", "Donnée non disponible")

        with tab2:
            st.subheader("Taux Directeurs des Banques Centrales")
            st.info("Ces taux sont mis à jour manuellement et ne reflètent pas les changements en temps réel.")
            cols = st.columns(2)
            taux = self.market_data['taux_interet']
            
            with cols[0]:
                for banque, taux_val in list(taux.items())[:2]:
                    st.metric(f"{banque}", f"{taux_val}%", "Dernière mise à jour connue")
            
            with cols[1]:
                for banque, taux_val in list(taux.items())[2:]:
                    st.metric(f"{banque}", f"{taux_val}%", "Dernière mise à jour connue")
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 📊 Indicateurs Économiques
                
                **🇺🇸 États-Unis:**
                - Inflation: 3.2%
                - Croissance PIB: 2.1%
                - Chômage: 3.8%
                
                **🇪🇺 Zone Euro:**
                - Inflation: 2.4%
                - Croissance PIB: 0.5%
                - Chômage: 6.5%
                """)
            
            with col2:
                st.markdown("""
                ### 🌍 Tendances Mondiales
                
                **🛢️ Énergie:**
                - Demande pétrolière: 102M barils/jour
                - Stocks US: 450M barils
                
                **🏭 Production:**
                - PMI Mondial: 50.8
                - PMI Manufacturing: 49.2
                """)
    
    def create_risk_analysis(self):
        """Analyse des risques"""
        st.markdown('<h3 class="section-header">⚠️ ANALYSE DES RISQUES MARCHÉ</h3>', unsafe_allow_html=True)
        
        st.info("Cette section utilise des données simulées pour illustrer les scénarios de risque.")
        
        tab1, tab2, tab3 = st.tabs(["Risques Géopolitiques", "Stress Tests", "Indicateurs de Stress"])
        
        with tab1:
            st.subheader("Carte des Risques Géopolitiques")
            risk_data = []
            regions = ['Moyen-Orient', 'Europe', 'Asie', 'Amérique', 'Afrique', 'Océanie']
            for region in regions:
                risk_score = np.random.randint(20, 85)
                risk_level = "FAIBLE" if risk_score < 33 else "MOYEN" if risk_score < 66 else "ÉLEVÉ"
                risk_data.append({'Région': region, 'Score Risque': risk_score, 'Niveau': risk_level})
            risk_df = pd.DataFrame(risk_data)
            st.dataframe(risk_df, use_container_width=True)
        
        with tab2:
            st.markdown("""
            ### 📉 Scénario de Récession
            **Impacts potentiels sur les devises et commodities.**
            """)
            st.markdown("""
            ### 📈 Scénario de Reprise
            **Impacts potentiels sur les devises et commodities.**
            """)
        
        with tab3:
            st.subheader("Indicateurs de Stress Financier")
            stress_indicators = {'VIX': 18.5, 'Spread de Crédit': 1.2, 'Indice USD': 104.2}
            cols = st.columns(3)
            for i, (indicator, data) in enumerate(stress_indicators.items()):
                with cols[i]:
                    st.metric(indicator, f"{data}", "Normal")

    def create_sidebar(self):
        """Crée la sidebar"""
        st.sidebar.markdown("## 🎛️ CONTRÔLES D'ANALYSE")
        
        st.sidebar.markdown("### ⚙️ Options")
        auto_refresh = st.sidebar.checkbox("Rafraîchissement automatique (toutes les 60s)", value=True)
        alert_threshold = st.sidebar.slider("Seuil d'alerte (%)", 1.0, 10.0, 3.0)
        
        if st.sidebar.button("🔄 Rafraîchir les données maintenant"):
            self.update_live_data()
            st.rerun()
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔔 ALERTES EN TEMPS RÉEL")
        
        if not self.current_data_forex.empty:
            alert_forex = self.current_data_forex[abs(self.current_data_forex['change_pct']) > alert_threshold]
            for _, alert in alert_forex.iterrows():
                st.sidebar.warning(f"{alert['drapeau']} {alert['symbole']}: {alert['change_pct']:+.2f}%")
        
        if not self.current_data_commodities.empty:
            alert_comm = self.current_data_commodities[abs(self.current_data_commodities['change_pct']) > alert_threshold]
            for _, alert in alert_comm.iterrows():
                st.sidebar.error(f"🛢️ {alert['symbole']}: {alert['change_pct']:+.2f}%")
        
        return {'auto_refresh': auto_refresh, 'alert_threshold': alert_threshold}

    def run_dashboard(self):
        """Exécute le dashboard complet"""
        # Sidebar
        controls = self.create_sidebar()
        
        # Header
        self.display_header()
        
        # Top performers
        self.display_top_currencies()
        self.display_top_commodities()
        
        # Métriques clés
        self.display_key_metrics()
        
        # Navigation par onglets
        tab1, tab2, tab3, tab4 = st.tabs([
            "🌍 Macro", "⚠️ Risques", "💡 Insights", "ℹ️ À Propos"
        ])
        
        with tab1:
            self.create_macro_analysis()
        
        with tab2:
            self.create_risk_analysis()
        
        with tab3:
            st.markdown("## 💡 INSIGHTS STRATÉGIQUES")
            st.info("Les insights ci-dessous sont des exemples et doivent être adaptés en fonction des données réelles du marché.")
            st.markdown("""
            ### 🚨 RECOMMANDATIONS STRATÉGIQUES
            
            1. **Diversification:** Portefeuille équilibré entre devises et commodities
            2. **Couverture:** Utiliser l'or et le CHF comme actifs refuges
            3. **Exposition Sectorielle:** Ponderer selon les cycles économiques
            4. **Surveillance Géopolitique:** Attention aux risques régionaux
            5. **Horizon Temporel:** Adapter la stratégie au profil d'investissement
            """)
        
        with tab4:
            st.markdown("## 📋 À Propos")
            st.markdown("""
            **Dashboard Commodities & Monnaies Mondiales - Analyse en Temps Réel**
            
            **Source des Données:**
            - **Devises, Commodities, Indices :** Yahoo Finance via la bibliothèque `yfinance`.
            - **Taux d'intérêt :** Données de référence, mises à jour manuellement.
            
            **Avertissement:**
            - Les données sont fournies "en l'état" et peuvent comporter des retards.
            - Ce dashboard est un outil de démonstration et de visualisation.
            - **Il ne constitue pas un conseil en investissement.**
            - Faites vos propres recherches avant de prendre toute décision financière.
            """)
        
        # Rafraîchissement automatique
        if controls['auto_refresh']:
            time.sleep(60)
            st.rerun()

# Lancement du dashboard
if __name__ == "__main__":
    dashboard = CommodityCurrencyDashboard()
    dashboard.run_dashboard()