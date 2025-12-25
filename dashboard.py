import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="QuantPro Dashboard")

# --- SIDEBAR: CONTROLS ---
st.sidebar.header("Strategy Parameters")
ticker = st.sidebar.text_input("Stock Symbol", value="AAPL").upper()
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("today"))

st.sidebar.markdown("---")
st.sidebar.subheader("Moving Averages")
fast_window = st.sidebar.slider("Fast SMA (Days)", min_value=5, max_value=50, value=10)
slow_window = st.sidebar.slider("Slow SMA (Days)", min_value=20, max_value=200, value=30)


# --- MAIN LOGIC: DATA FETCHING ---
@st.cache_data
def get_data(ticker, start, end):
    try:
        df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
        # Fix for multi-index columns in newer yfinance versions
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None


# Load Data
data = get_data(ticker, start_date, end_date)

if data is not None and not data.empty:
    # --- CALCULATIONS ---
    # Calculate Indicators manually for the visual dashboard
    data['Fast_SMA'] = data['Close'].rolling(window=fast_window).mean()
    data['Slow_SMA'] = data['Close'].rolling(window=slow_window).mean()

    # Calculate Strategy Signals (1 = Buy, -1 = Sell)
    data['Signal'] = 0.0
    data['Signal'][fast_window:] = \
        pd.Series(data['Fast_SMA'][fast_window:] > data['Slow_SMA'][fast_window:]).astype(int)
    data['Position'] = data['Signal'].diff()

    # --- DASHBOARD LAYOUT ---
    st.title(f"📊 QuantPro System: {ticker}")

    # Top-level metrics
    last_close = data['Close'].iloc[-1]
    prev_close = data['Close'].iloc[-2]
    daily_change = last_close - prev_close
    pct_change = (daily_change / prev_close) * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Last Price", f"${last_close:.2f}", f"{daily_change:.2f} ({pct_change:.2f}%)")
    col2.metric("Fast SMA", f"{data['Fast_SMA'].iloc[-1]:.2f}")
    col3.metric("Slow SMA", f"{data['Slow_SMA'].iloc[-1]:.2f}")
    col4.metric("Market Signal", "BULLISH" if data['Fast_SMA'].iloc[-1] > data['Slow_SMA'].iloc[-1] else "BEARISH")

    # --- PLOTTING (PROFESSIONAL CHART) ---
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03, subplot_titles=('Price Action & Strategy', 'Volume'),
                        row_width=[0.2, 0.7])

    # 1. Candlestick Chart
    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['Open'], high=data['High'],
                                 low=data['Low'], close=data['Close'], name='Price'),
                  row=1, col=1)

    # 2. Moving Averages
    fig.add_trace(go.Scatter(x=data.index, y=data['Fast_SMA'], line=dict(color='orange', width=1), name='Fast SMA'),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['Slow_SMA'], line=dict(color='blue', width=1), name='Slow SMA'),
                  row=1, col=1)

    # 3. Buy/Sell Markers (Arrows)
    # Buy Signals
    buy_signals = data[data['Position'] == 1]
    fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Close'],
                             mode='markers', marker=dict(symbol='triangle-up', size=10, color='green'),
                             name='Buy Signal'),
                  row=1, col=1)

    # Sell Signals
    sell_signals = data[data['Position'] == -1]
    fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['Close'],
                             mode='markers', marker=dict(symbol='triangle-down', size=10, color='red'),
                             name='Sell Signal'),
                  row=1, col=1)

    # 4. Volume Bar Chart
    fig.add_trace(go.Bar(x=data.index, y=data['Volume'], showlegend=False), row=2, col=1)

    # Layout Styling
    fig.update_layout(height=700, xaxis_rangeslider_visible=False, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # --- RAW DATA TABLE ---
    with st.expander("View Historical Data"):
        st.dataframe(data.sort_index(ascending=False))

else:
    st.error("No data found. Please check the stock ticker symbol.")