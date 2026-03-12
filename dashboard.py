from __future__ import annotations

import datetime as dt

import dash
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Input, Output, dash_table, dcc, html


def build_sample_sales_data(seed: int = 7) -> pd.DataFrame:
    rng = pd.Series(range(365)).sample(frac=1, random_state=seed)  # deterministic shuffle
    start = (dt.date.today() - dt.timedelta(days=364))
    dates = [start + dt.timedelta(days=int(i)) for i in range(365)]

    products = ["Starter", "Pro", "Business", "Enterprise"]
    regions = ["North", "South", "Center", "International"]
    channels = ["Web", "Partner", "Direct"]

    base = pd.DataFrame(
        {
            "date": dates,
            "product": [products[i % len(products)] for i in range(365)],
            "region": [regions[(i // 2) % len(regions)] for i in range(365)],
            "channel": [channels[(i // 3) % len(channels)] for i in range(365)],
        }
    )

    # Add a bit of realistic seasonality + noise (still deterministic)
    t = pd.Series(range(365))
    season = 1.0 + 0.25 * pd.Series(np.sin(2 * np.pi * t / 30.0))  # monthly-ish
    noise = (rng.reset_index(drop=True) % 17) / 20.0  # 0..0.8

    price_map = {"Starter": 29, "Pro": 79, "Business": 199, "Enterprise": 499}
    base["orders"] = (18 * season + 6 * noise).round().astype(int)
    base["orders"] = base["orders"].clip(lower=0)
    base["aov_usd"] = base["product"].map(price_map).astype(float) * (0.9 + 0.25 * noise)
    base["revenue_usd"] = (base["orders"] * base["aov_usd"]).round(2)

    return base


df = build_sample_sales_data()
df["date"] = pd.to_datetime(df["date"])

app = dash.Dash(__name__, title="Sales Dashboard")
server = app.server

app.layout = html.Div(
    style={"fontFamily": "system-ui, -apple-system, Segoe UI, Roboto, Arial", "padding": "18px"},
    children=[
        html.Div(
            style={"display": "flex", "alignItems": "baseline", "justifyContent": "space-between"},
            children=[
                html.Div(
                    children=[
                        html.H2("Sales Dashboard", style={"margin": "0"}),
                        html.Div(
                            "Interactive demo dashboard (Dash + Plotly).",
                            style={"color": "#5b6573", "marginTop": "6px"},
                        ),
                    ]
                ),
                html.Div(id="last-updated", style={"color": "#5b6573"}),
            ],
        ),
        html.Hr(style={"margin": "14px 0 18px 0", "opacity": "0.35"}),
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "320px 1fr", "gap": "16px"},
            children=[
                html.Div(
                    style={
                        "border": "1px solid #e6e8eb",
                        "borderRadius": "12px",
                        "padding": "14px",
                        "background": "#fbfcfe",
                        "height": "fit-content",
                    },
                    children=[
                        html.H4("Filters", style={"marginTop": 0, "marginBottom": "10px"}),
                        html.Label("Date range", style={"fontWeight": 600}),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=df["date"].min().date(),
                            max_date_allowed=df["date"].max().date(),
                            start_date=(df["date"].max() - pd.Timedelta(days=60)).date(),
                            end_date=df["date"].max().date(),
                            display_format="YYYY-MM-DD",
                            style={"marginTop": "6px", "marginBottom": "14px"},
                        ),
                        html.Label("Product", style={"fontWeight": 600}),
                        dcc.Dropdown(
                            id="product",
                            options=[{"label": "All", "value": "__all__"}]
                            + [{"label": p, "value": p} for p in sorted(df["product"].unique())],
                            value="__all__",
                            clearable=False,
                            style={"marginTop": "6px", "marginBottom": "14px"},
                        ),
                        html.Label("Region", style={"fontWeight": 600}),
                        dcc.Dropdown(
                            id="region",
                            options=[{"label": "All", "value": "__all__"}]
                            + [{"label": r, "value": r} for r in sorted(df["region"].unique())],
                            value="__all__",
                            clearable=False,
                            style={"marginTop": "6px", "marginBottom": "14px"},
                        ),
                        html.Label("Channel", style={"fontWeight": 600}),
                        dcc.Dropdown(
                            id="channel",
                            options=[{"label": "All", "value": "__all__"}]
                            + [{"label": c, "value": c} for c in sorted(df["channel"].unique())],
                            value="__all__",
                            clearable=False,
                            style={"marginTop": "6px", "marginBottom": "14px"},
                        ),
                        html.Button(
                            "Reset filters",
                            id="reset",
                            n_clicks=0,
                            style={
                                "width": "100%",
                                "border": "1px solid #d7dbe0",
                                "background": "white",
                                "borderRadius": "10px",
                                "padding": "10px 12px",
                                "cursor": "pointer",
                            },
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(
                            style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)", "gap": "12px"},
                            children=[
                                html.Div(id="kpi-revenue", className="kpi-card"),
                                html.Div(id="kpi-orders", className="kpi-card"),
                                html.Div(id="kpi-aov", className="kpi-card"),
                                html.Div(id="kpi-days", className="kpi-card"),
                            ],
                        ),
                        html.Div(style={"height": "12px"}),
                        html.Div(
                            style={"display": "grid", "gridTemplateColumns": "1.4fr 1fr", "gap": "12px"},
                            children=[
                                html.Div(
                                    style={
                                        "border": "1px solid #e6e8eb",
                                        "borderRadius": "12px",
                                        "padding": "10px",
                                    },
                                    children=[
                                        html.Div(
                                            "Revenue over time",
                                            style={"fontWeight": 700, "margin": "4px 6px 10px 6px"},
                                        ),
                                        dcc.Graph(id="rev-timeseries", config={"displayModeBar": False}),
                                    ],
                                ),
                                html.Div(
                                    style={
                                        "border": "1px solid #e6e8eb",
                                        "borderRadius": "12px",
                                        "padding": "10px",
                                    },
                                    children=[
                                        html.Div(
                                            "Revenue by product",
                                            style={"fontWeight": 700, "margin": "4px 6px 10px 6px"},
                                        ),
                                        dcc.Graph(id="rev-by-product", config={"displayModeBar": False}),
                                    ],
                                ),
                            ],
                        ),
                        html.Div(style={"height": "12px"}),
                        html.Div(
                            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px"},
                            children=[
                                html.Div(
                                    style={
                                        "border": "1px solid #e6e8eb",
                                        "borderRadius": "12px",
                                        "padding": "10px",
                                    },
                                    children=[
                                        html.Div(
                                            "Revenue share by region",
                                            style={"fontWeight": 700, "margin": "4px 6px 10px 6px"},
                                        ),
                                        dcc.Graph(id="rev-by-region", config={"displayModeBar": False}),
                                    ],
                                ),
                                html.Div(
                                    style={
                                        "border": "1px solid #e6e8eb",
                                        "borderRadius": "12px",
                                        "padding": "10px",
                                    },
                                    children=[
                                        html.Div(
                                            "Transactions",
                                            style={"fontWeight": 700, "margin": "4px 6px 10px 6px"},
                                        ),
                                        dash_table.DataTable(
                                            id="table",
                                            page_size=10,
                                            sort_action="native",
                                            filter_action="none",
                                            style_table={"overflowX": "auto"},
                                            style_cell={
                                                "fontFamily": "system-ui, -apple-system, Segoe UI, Roboto, Arial",
                                                "fontSize": "13px",
                                                "padding": "8px",
                                                "whiteSpace": "nowrap",
                                            },
                                            style_header={"fontWeight": 700, "backgroundColor": "#f4f6f8"},
                                            style_data_conditional=[
                                                {"if": {"row_index": "odd"}, "backgroundColor": "#fbfcfe"}
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        dcc.Interval(id="tick", interval=60_000, n_intervals=0),
                    ],
                ),
            ],
        ),
        html.Style(
            """
            .kpi-card{
              border:1px solid #e6e8eb;
              border-radius:12px;
              padding:12px 14px;
              background:white;
              min-height:74px;
            }
            .kpi-title{ color:#5b6573; font-size:12px; font-weight:700; letter-spacing:0.02em; }
            .kpi-value{ font-size:24px; font-weight:800; margin-top:6px; }
            .kpi-sub{ color:#5b6573; font-size:12px; margin-top:2px; }
            """
        ),
    ],
)


def _apply_filter(d: pd.DataFrame, col: str, value: str) -> pd.DataFrame:
    if value == "__all__" or value is None:
        return d
    return d[d[col] == value]


def _fmt_money(x: float) -> str:
    return f"${x:,.0f}"


@app.callback(
    Output("product", "value"),
    Output("region", "value"),
    Output("channel", "value"),
    Input("reset", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_n_clicks: int):
    return "__all__", "__all__", "__all__"


@app.callback(
    Output("kpi-revenue", "children"),
    Output("kpi-orders", "children"),
    Output("kpi-aov", "children"),
    Output("kpi-days", "children"),
    Output("rev-timeseries", "figure"),
    Output("rev-by-product", "figure"),
    Output("rev-by-region", "figure"),
    Output("table", "data"),
    Output("table", "columns"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("product", "value"),
    Input("region", "value"),
    Input("channel", "value"),
)
def update_dashboard(start_date, end_date, product, region, channel):
    d = df.copy()
    if start_date:
        d = d[d["date"] >= pd.to_datetime(start_date)]
    if end_date:
        d = d[d["date"] <= pd.to_datetime(end_date)]
    d = _apply_filter(d, "product", product)
    d = _apply_filter(d, "region", region)
    d = _apply_filter(d, "channel", channel)

    revenue = float(d["revenue_usd"].sum())
    orders = int(d["orders"].sum())
    aov = float((d["revenue_usd"].sum() / max(orders, 1)))
    days = int(d["date"].nunique())

    kpi_rev = [
        html.Div("REVENUE", className="kpi-title"),
        html.Div(_fmt_money(revenue), className="kpi-value"),
        html.Div("Sum of revenue in range", className="kpi-sub"),
    ]
    kpi_orders = [
        html.Div("ORDERS", className="kpi-title"),
        html.Div(f"{orders:,}", className="kpi-value"),
        html.Div("Total orders", className="kpi-sub"),
    ]
    kpi_aov = [
        html.Div("AOV", className="kpi-title"),
        html.Div(_fmt_money(aov), className="kpi-value"),
        html.Div("Avg order value", className="kpi-sub"),
    ]
    kpi_days = [
        html.Div("DAYS", className="kpi-title"),
        html.Div(f"{days:,}", className="kpi-value"),
        html.Div("Distinct days", className="kpi-sub"),
    ]

    by_day = d.groupby("date", as_index=False)["revenue_usd"].sum().sort_values("date")
    fig_ts = px.area(by_day, x="date", y="revenue_usd", labels={"revenue_usd": "Revenue (USD)", "date": ""})
    fig_ts.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=310)

    by_product = d.groupby("product", as_index=False)["revenue_usd"].sum().sort_values("revenue_usd", ascending=False)
    fig_prod = px.bar(by_product, x="product", y="revenue_usd", labels={"revenue_usd": "Revenue (USD)", "product": ""})
    fig_prod.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=310)

    by_region = d.groupby("region", as_index=False)["revenue_usd"].sum().sort_values("revenue_usd", ascending=False)
    fig_region = px.pie(by_region, names="region", values="revenue_usd", hole=0.45)
    fig_region.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=310, legend_title_text="")

    table = d.sort_values("date", ascending=False).head(250).copy()
    table["date"] = table["date"].dt.strftime("%Y-%m-%d")
    table["aov_usd"] = table["aov_usd"].map(lambda x: f"{x:,.2f}")
    table["revenue_usd"] = table["revenue_usd"].map(lambda x: f"{x:,.2f}")

    columns = [
        {"name": "Date", "id": "date"},
        {"name": "Product", "id": "product"},
        {"name": "Region", "id": "region"},
        {"name": "Channel", "id": "channel"},
        {"name": "Orders", "id": "orders"},
        {"name": "AOV (USD)", "id": "aov_usd"},
        {"name": "Revenue (USD)", "id": "revenue_usd"},
    ]

    return kpi_rev, kpi_orders, kpi_aov, kpi_days, fig_ts, fig_prod, fig_region, table.to_dict("records"), columns


@app.callback(Output("last-updated", "children"), Input("tick", "n_intervals"))
def show_last_updated(_n):
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"Last updated: {now}"


if __name__ == "__main__":
    app.run_server(debug=True)