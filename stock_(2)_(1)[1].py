import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Stock Market Dashboard", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS Styling
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #f5f7fa;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 2rem;
    }
    
    /* Stock card styling */
    .stock-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e8ebed;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .stock-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    /* Price styling */
    .price-positive {
        color: #10b981;
        font-weight: 600;
    }
    
    .price-negative {
        color: #ef4444;
        font-weight: 600;
    }
    
    /* Metric labels */
    .metric-label {
        font-size: 13px;
        color: #6b7280;
        font-weight: 500;
        margin-bottom: 4px;
    }
    
    .metric-value {
        font-size: 16px;
        color: #111827;
        font-weight: 600;
    }
    
    /* Header styling */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Search results */
    .search-result {
        background: white;
        padding: 16px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .search-result:hover {
        background: #f9fafb;
        border-left-color: #764ba2;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Button styling */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []
if 'selected_market' not in st.session_state:
    st.session_state.selected_market = "Indian Stocks (NSE)"

# Credentials
DUMMY_USERNAME = "admin"
DUMMY_PASSWORD = "password123"

# Stock databases
STOCK_DATABASE = {
    "Indian Stocks (NSE)": {
        "RELIANCE.NS": "Reliance Industries Ltd",
        "TCS.NS": "Tata Consultancy Services",
        "INFY.NS": "Infosys Limited",
        "HDFCBANK.NS": "HDFC Bank Ltd",
        "ICICIBANK.NS": "ICICI Bank Ltd",
        "HINDUNILVR.NS": "Hindustan Unilever",
        "SBIN.NS": "State Bank of India",
        "BHARTIARTL.NS": "Bharti Airtel Ltd",
        "ITC.NS": "ITC Limited",
        "KOTAKBANK.NS": "Kotak Mahindra Bank",
        "LT.NS": "Larsen & Toubro",
        "AXISBANK.NS": "Axis Bank Ltd",
        "TATAMOTORS.NS": "Tata Motors Ltd",
        "WIPRO.NS": "Wipro Limited",
        "MARUTI.NS": "Maruti Suzuki India"
    },
    "US Stocks": {
        "AAPL": "Apple Inc",
        "MSFT": "Microsoft Corporation",
        "GOOGL": "Alphabet Inc Class A",
        "AMZN": "Amazon.com Inc",
        "NVDA": "NVIDIA Corporation",
        "TSLA": "Tesla Inc",
        "META": "Meta Platforms Inc",
        "BRK-B": "Berkshire Hathaway",
        "JPM": "JPMorgan Chase & Co",
        "V": "Visa Inc",
        "WMT": "Walmart Inc",
        "MA": "Mastercard Inc",
        "PG": "Procter & Gamble Co",
        "DIS": "Walt Disney Co",
        "NFLX": "Netflix Inc"
    }
}

def login_page():
    """Professional login page"""
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown("""
        <div style='background: white; padding: 50px; border-radius: 16px; 
                    box-shadow: 0 8px 24px rgba(0,0,0,0.12); text-align: center;'>
            <h1 style='color: #667eea; margin-bottom: 10px;'>📊 Stock Dashboard</h1>
            <p style='color: #6b7280; font-size: 16px; margin-bottom: 40px;'>
                Professional Stock Market Analytics
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container():
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Login", use_container_width=True, type="primary"):
                if username == DUMMY_USERNAME and password == DUMMY_PASSWORD:
                    st.session_state.logged_in = True
                    st.success("✓ Login successful!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("✗ Invalid credentials")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("💡 Demo credentials → username: admin | password: password123")

@st.cache_data(ttl=30)
def get_stock_data(ticker):
    """Fetch stock data"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1mo", interval="1d")
        
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        prev_close = info.get('previousClose', current_price)
        change = current_price - prev_close
        change_percent = (change / prev_close * 100) if prev_close else 0
        
        return {
            'symbol': ticker,
            'name': info.get('longName', info.get('shortName', ticker)),
            'price': current_price,
            'open': info.get('regularMarketOpen', 0),
            'high': info.get('dayHigh', 0),
            'low': info.get('dayLow', 0),
            'volume': info.get('volume', 0),
            'prev_close': prev_close,
            'change': change,
            'change_percent': change_percent,
            'history': hist,
            'currency': '₹' if '.NS' in ticker or '.BO' in ticker else '$',
            'market_cap': info.get('marketCap', 0)
        }
    except:
        return None

def format_number(num):
    """Format large numbers"""
    if num >= 1e12:
        return f"{num/1e12:.2f}T"
    elif num >= 1e9:
        return f"{num/1e9:.2f}B"
    elif num >= 1e6:
        return f"{num/1e6:.2f}M"
    elif num >= 1e3:
        return f"{num/1e3:.2f}K"
    return f"{num:.2f}"

def create_chart(data):
    """Create professional chart"""
    if data['history'].empty:
        return None
    
    color = '#10b981' if data['change'] >= 0 else '#ef4444'
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['history'].index,
        y=data['history']['Close'],
        mode='lines',
        name='Price',
        line=dict(color=color, width=2.5),
        fill='tozeroy',
        fillcolor=f'rgba({"16, 185, 129" if data["change"] >= 0 else "239, 68, 68"}, 0.1)'
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=False,
            showline=False,
            zeroline=False,
            tickfont=dict(size=10, color='#9ca3af')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#f3f4f6',
            showline=False,
            zeroline=False,
            tickfont=dict(size=10, color='#9ca3af')
        ),
        hovermode='x unified',
        showlegend=False
    )
    
    return fig

def display_stock_card(data):
    """Display professional stock card"""
    if not data:
        return
    
    change_class = "price-positive" if data['change'] >= 0 else "price-negative"
    arrow = "↑" if data['change'] >= 0 else "↓"
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class='stock-card'>
            <div style='display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px;'>
                <div>
                    <h2 style='margin: 0; color: #111827; font-size: 24px;'>{data['symbol']}</h2>
                    <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>{data['name']}</p>
                </div>
                <div style='text-align: right;'>
                    <h1 style='margin: 0; color: #111827; font-size: 32px; font-weight: 700;'>
                        {data['currency']}{data['price']:.2f}
                    </h1>
                    <p class='{change_class}' style='margin: 4px 0 0 0; font-size: 16px;'>
                        {arrow} {data['currency']}{abs(data['change']):.2f} ({abs(data['change_percent']):.2f}%)
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Chart
        fig = create_chart(data)
        if fig:
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{data['symbol']}_{time.time()}")
    
    with col2:
        st.markdown(f"""
        <div class='stock-card' style='height: 100%;'>
            <div style='margin-bottom: 20px;'>
                <div class='metric-label'>OPEN</div>
                <div class='metric-value'>{data['currency']}{data['open']:.2f}</div>
            </div>
            <div style='margin-bottom: 20px;'>
                <div class='metric-label'>HIGH</div>
                <div class='metric-value'>{data['currency']}{data['high']:.2f}</div>
            </div>
            <div style='margin-bottom: 20px;'>
                <div class='metric-label'>LOW</div>
                <div class='metric-value'>{data['currency']}{data['low']:.2f}</div>
            </div>
            <div style='margin-bottom: 20px;'>
                <div class='metric-label'>VOLUME</div>
                <div class='metric-value'>{format_number(data['volume'])}</div>
            </div>
            <div>
                <div class='metric-label'>MARKET CAP</div>
                <div class='metric-value'>{data['currency']}{format_number(data['market_cap'])}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def search_stocks(query, market):
    """Smart search function"""
    if not query:
        return []
    
    query = query.upper()
    results = []
    
    for symbol, name in STOCK_DATABASE[market].items():
        if query in symbol.upper() or query in name.upper():
            results.append((symbol, name))
    
    return results[:10]

def main_app():
    """Main dashboard"""
    
    # Header
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown("""
        <div class='dashboard-header'>
            <h1 style='margin: 0; font-size: 32px;'>Stock Market Dashboard</h1>
            <p style='margin: 8px 0 0 0; opacity: 0.9; font-size: 15px;'>
                Real-time market data and analytics
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            st.session_state.logged_in = False
            st.rerun()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 Market Selection")
        market = st.radio(
            "Choose market",
            list(STOCK_DATABASE.keys()),
            index=0,
            label_visibility="collapsed"
        )
        st.session_state.selected_market = market
        
        st.markdown("---")
        
        st.markdown("### ⭐ Watchlist")
        if st.session_state.watchlist:
            for symbol in st.session_state.watchlist:
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    if st.button(symbol, key=f"watch_{symbol}", use_container_width=True):
                        st.session_state.search_query = symbol
                        st.rerun()
                with col_b:
                    if st.button("×", key=f"remove_{symbol}"):
                        st.session_state.watchlist.remove(symbol)
                        st.rerun()
        else:
            st.info("No stocks added")
    
    # Smart Search
    st.markdown("### 🔍 Search Stocks")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        search_query = st.text_input(
            "Search",
            placeholder=f"Type stock name or symbol (e.g., {'Reliance, TCS' if 'Indian' in market else 'Apple, Tesla'})",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        clear_btn = st.button("Clear", use_container_width=True)
        if clear_btn:
            st.rerun()
    
    # Search Results
    if search_query:
        results = search_stocks(search_query, market)
        
        if results:
            st.markdown(f"**Found {len(results)} result(s)**")
            
            cols = st.columns(min(len(results), 3))
            
            for idx, (symbol, name) in enumerate(results):
                with cols[idx % 3]:
                    col_a, col_b = st.columns([3, 1])
                    
                    with col_a:
                        if st.button(f"**{symbol}**\n{name[:25]}", key=f"result_{symbol}", use_container_width=True):
                            with st.spinner("Loading..."):
                                data = get_stock_data(symbol)
                                if data:
                                    st.markdown("---")
                                    display_stock_card(data)
                                    
                                    if symbol not in st.session_state.watchlist:
                                        if st.button("⭐ Add to Watchlist", key=f"add_{symbol}"):
                                            st.session_state.watchlist.append(symbol)
                                            st.rerun()
                    
                    with col_b:
                        quick_data = get_stock_data(symbol)
                        if quick_data:
                            change_emoji = "📈" if quick_data['change'] >= 0 else "📉"
                            st.markdown(f"<div style='text-align: center; font-size: 20px;'>{change_emoji}</div>", unsafe_allow_html=True)
        else:
            st.warning(f"No results found for '{search_query}'")
    
    # Trending Stocks
    st.markdown("---")
    st.markdown(f"### 🔥 Trending Stocks - {market}")
    
    trending = list(STOCK_DATABASE[market].items())[:6]
    
    for i in range(0, len(trending), 2):
        cols = st.columns(2)
        
        for j in range(2):
            if i + j < len(trending):
                symbol, name = trending[i + j]
                
                with cols[j]:
                    with st.spinner(f"Loading {symbol}..."):
                        data = get_stock_data(symbol)
                        if data:
                            display_stock_card(data)
                            
                            if symbol not in st.session_state.watchlist:
                                if st.button(f"⭐ Add {symbol} to Watchlist", key=f"add_trending_{symbol}", use_container_width=True):
                                    st.session_state.watchlist.append(symbol)
                                    st.rerun()

# Main execution
if st.session_state.logged_in:
    main_app()
else:
    login_page()