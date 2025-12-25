import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from quant_system import run_backtest

st.set_page_config(layout="wide", page_title="QuantPro ZAR Dashboard", page_icon="📈")

# --- SIDEBAR ---
st.sidebar.header("Strategy Settings (ZAR)")
ticker = st.sidebar.text_input("Stock Symbol (e.g. AAPL or NPN.JO)", value="AAPL").upper()
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("today"))

st.sidebar.markdown("---")
fast_window = st.sidebar.slider("Fast SMA (Days)", 5, 50, 10)
slow_window = st.sidebar.slider("Slow SMA (Days)", 20, 200, 30)
run_engine = st.sidebar.button("🚀 Run Backtest Engine")

# --- MAIN ---
st.title(f"📊 QuantPro System: {ticker}")

if run_engine:
    with st.spinner('Running Engine in Rands...'):
        try:
            data, final_value = run_backtest(ticker, start_date, end_date, fast_window, slow_window)

            # Calculation based on R1,000,000 starting cash
            start_cash = 1000000.0
            total_profit = final_value - start_cash
            roi = (total_profit / start_cash) * 100

            # Metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("Final Portfolio Value", f"R {final_value:,.2f}")
            c2.metric("Total ROI", f"{roi:.2f}%", delta=f"R {total_profit:,.2f}")

            last_sig = data['Crossover'].iloc[-1]
            status = "BUY" if last_sig > 0 else "SELL" if last_sig < 0 else "NEUTRAL"
            c3.metric("Current Signal", status)

            # Plotting
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                vertical_spacing=0.05, row_width=[0.2, 0.8],
                                subplot_titles=("Price & Indicators", "Volume"))

            # Price & SMAs
            fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'],
                                         low=data['Low'], close=data['Close'], name="Price"), row=1, col=1)
            fig.add_trace(go.Scatter(x=data.index, y=data['Fast_SMA'], name="Fast SMA", line=dict(color='orange')), row=1, col=1)
            fig.add_trace(go.Scatter(x=data.index, y=data['Slow_SMA'], name="Slow SMA", line=dict(color='blue')), row=1, col=1)

            # Signals
            buys = data[data['Crossover'] > 0]
            sells = data[data['Crossover'] < 0]
            fig.add_trace(go.Scatter(x=buys.index, y=buys['Close'], mode='markers',
                                     marker=dict(symbol='triangle-up', size=12, color='lime'), name="Buy Signal"), row=1, col=1)
            fig.add_trace(go.Scatter(x=sells.index, y=sells['Close'], mode='markers',
                                     marker=dict(symbol='triangle-down', size=12, color='red'), name="Sell Signal"), row=1, col=1)

            # Volume
            fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name="Volume", marker_color='white', opacity=0.3), row=2, col=1)

            fig.update_layout(height=700, template="plotly_dark", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.info("Adjust parameters and click the button to see results in ZAR.")
