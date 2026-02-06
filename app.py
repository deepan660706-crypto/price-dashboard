import pandas as pd
from datetime import timedelta
from dash import Dash, dcc, html, Input, Output, ctx
import plotly.express as px

# -----------------------------
# STEP 1 — LOAD EXCEL DATA
# -----------------------------
file_path = "product_price_demo_data_2025.xlsx"

df = pd.read_excel(file_path)
df["Date"] = pd.to_datetime(df["Date"])

products = df["Product"].unique()

# -----------------------------
# STEP 2 — DASH APP UI
# -----------------------------
app = Dash(__name__)

app.layout = html.Div([

    html.H2("📊 Product Price Tracker (Excel Source)", style={"textAlign": "center"}),

    html.Div([
        html.Button("1 Month", id="btn-1m", n_clicks=0),
        html.Button("6 Months", id="btn-6m", n_clicks=0),
        html.Button("All", id="btn-all", n_clicks=0),

        dcc.Dropdown(
            id="product-dropdown",
            options=[{"label": p, "value": p} for p in products],
            value=products[0],
            clearable=False,
            style={"width": "250px"}
        )
    ],
    style={
        "display": "flex",
        "gap": "15px",
        "justifyContent": "center",
        "marginBottom": "20px"
    }),

    dcc.Graph(id="price-graph"),

    # 📊 SINGLE LIGHT KPI BAR
    html.Div(id="stats-bar", style={
        "marginTop": "20px",
        "padding": "15px",
        "background": "#f4f6f8",
        "borderRadius": "8px",
        "fontSize": "18px",
        "textAlign": "center",
        "boxShadow": "0px 2px 6px rgba(0,0,0,0.1)"
    })

])

# -----------------------------
# STEP 3 — INTERACTIVE FILTER LOGIC
# -----------------------------
@app.callback(
    Output("price-graph", "figure"),
    Output("stats-bar", "children"),
    Input("product-dropdown", "value"),
    Input("btn-1m", "n_clicks"),
    Input("btn-6m", "n_clicks"),
    Input("btn-all", "n_clicks"),
)
def update_graph(selected_product, btn1, btn6, btnall):

    filtered_df = df[df["Product"] == selected_product]

    triggered = ctx.triggered_id

    if triggered == "btn-1m":
        range_selected = "1m"
    elif triggered == "btn-6m":
        range_selected = "6m"
    else:
        range_selected = "all"

    today = filtered_df["Date"].max()

    if range_selected == "1m":
        start_date = today - timedelta(days=30)
        filtered_df = filtered_df[filtered_df["Date"] >= start_date]

    elif range_selected == "6m":
        start_date = today - timedelta(days=180)
        filtered_df = filtered_df[filtered_df["Date"] >= start_date]

    # -----------------------------
    # Graph
    # -----------------------------
    fig = px.line(
        filtered_df,
        x="Date",
        y="Price_USD",
        markers=True,
        title=f"{selected_product} Price Trend",
    )

    fig.update_layout(
        yaxis_title="Price (USD)",
        xaxis_title="Date",
        template="plotly_dark",
        hovermode="x unified"
    )

    # -----------------------------
    # Stats calculation
    # -----------------------------
    highest_row = filtered_df.loc[filtered_df["Price_USD"].idxmax()]
    lowest_row = filtered_df.loc[filtered_df["Price_USD"].idxmin()]
    latest_row = filtered_df.sort_values("Date").iloc[-1]

    stats_bar = html.Div([
        html.Span(f"Product: {selected_product}   |   ", style={"fontWeight": "bold"}),

        html.Span(f"Highest: ${highest_row['Price_USD']} on {highest_row['Date'].date()}   |   ",
                  style={"color": "green"}),

        html.Span(f"Lowest: ${lowest_row['Price_USD']} on {lowest_row['Date'].date()}   |   ",
                  style={"color": "red"}),

        html.Span(f"Current: ${latest_row['Price_USD']} on {latest_row['Date'].date()}",
                  style={"color": "blue"})
    ])

    return fig, stats_bar


# -----------------------------
# RUN APP
# -----------------------------

server = app.server

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050)