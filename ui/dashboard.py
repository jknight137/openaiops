import dash
from dash import dcc, html, dash_table, Input, Output
import requests
import pandas as pd

API_URL = "http://localhost:8000/incidents"

app = dash.Dash(__name__)
app.title = "OpenAIOps Dashboard (Public Mode)"

def fetch_incidents():
    try:
        resp = requests.get(API_URL)
        if resp.status_code != 200:
            return pd.DataFrame()
        return pd.DataFrame(resp.json())
    except Exception as e:
        print(f"Error fetching incidents: {e}")
        return pd.DataFrame()

app.layout = html.Div([
    html.H1("OpenAIOps Dashboard (Public Mode)"),
    html.Div([
        html.Label("Status: "),
        dcc.Dropdown(
            id="status-filter",
            options=[
                {"label": "All", "value": ""},
                {"label": "Open", "value": "open"},
                {"label": "Acknowledged", "value": "ack"},
                {"label": "Resolved", "value": "resolved"}
            ],
            value=""
        ),
    ]),
    dcc.Interval(id="interval", interval=8 * 1000, n_intervals=0),
    dash_table.DataTable(
        id='incident-table',
        columns=[
            {"name": i, "id": i} for i in
            ["id", "type", "timestamp", "description", "status", "cpu", "mem", "latency", "log", "severity"]
        ],
        data=[],
        style_table={'overflowX': 'auto'},
        style_cell={'minWidth': 80, 'width': 100, 'maxWidth': 300},
        page_size=15,
        row_selectable="single"
    ),
    html.Div(id="incident-detail"),
    dcc.Graph(id="incidents-over-time"),
    html.Button("Acknowledge", id="ack-btn", n_clicks=0, disabled=True),
    html.Button("Resolve", id="resolve-btn", n_clicks=0, disabled=True)
])

@app.callback(
    Output("incident-table", "data"),
    Output("incidents-over-time", "figure"),
    Input("interval", "n_intervals"),
    Input("status-filter", "value"),
)
def update_table(n, status):
    try:
        params = {}
        if status:
            params["status"] = status
        resp = requests.get(API_URL, params=params)
        incidents = resp.json() if resp.status_code == 200 else []
        df = pd.DataFrame(incidents)
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            daily_counts = df.groupby(df["timestamp"].dt.date)["id"].count()
            chart = {
                "data": [{
                    "x": daily_counts.index.astype(str),
                    "y": daily_counts.values,
                    "type": "bar",
                    "name": "Incident Count"
                }],
                "layout": {"title": "Incidents Over Time"}
            }
        else:
            chart = {"data": [], "layout": {"title": "No Incidents Found"}}
        return df.to_dict("records"), chart
    except Exception as e:
        print(f"UI error: {e}")
        return [], {"data": [], "layout": {"title": "Error"}}

@app.callback(
    Output("incident-detail", "children"),
    Output("ack-btn", "disabled"),
    Output("resolve-btn", "disabled"),
    Input("incident-table", "selected_rows"),
    Input("incident-table", "data"),
)
def show_details(selected, data):
    if not selected or not data:
        return "", True, True
    inc = data[selected[0]]
    return html.Pre(str(inc)), inc["status"] != "open", inc["status"] == "resolved"

@app.callback(
    Output("interval", "disabled"),
    Input("ack-btn", "n_clicks"),
    Input("resolve-btn", "n_clicks"),
    Input("incident-table", "selected_rows"),
    Input("incident-table", "data"),
    prevent_initial_call=True
)
def ack_resolve(ack_n, res_n, selected, data):
    if not selected or not data:
        return False
    inc = data[selected[0]]
    if dash.callback_context.triggered_id == "ack-btn":
        requests.post(f"http://localhost:8000/incidents/{inc['id']}/ack")
    elif dash.callback_context.triggered_id == "resolve-btn":
        requests.post(f"http://localhost:8000/incidents/{inc['id']}/resolve")
    return False

if __name__ == '__main__':
    app.run(debug=True, port=8050)
