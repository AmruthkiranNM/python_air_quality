import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

from fetch_data import fetch_air_quality_data, fetch_historical_pollutant_data,fetch_air_quality_news
from visualize_data import process_pollutant_data

API_KEY = '3eeff1a081a4698bff38c3403b6ca26e'
NEWS_API_KEY ='40ac5653d6714bb1bc2770fb6e0759d2'

app = dash.Dash(__name__)
app.title = "Air Quality Dashboard"
app.css.config.serve_locally = True

app.layout = html.Div([
    html.H1("Real-Time Air Quality Dashboard"),

    html.Div([
        dcc.Input(
            id='city-input',
            type='text',
            value='Delhi',
            debounce=True,
            placeholder="Enter City Name"
        ),
        html.Button("Fetch Data", id='fetch-button', n_clicks=0)
    ], className="input-container"),

    html.Div(id="aqi-display", children=[]),

    html.Div([
        html.Div([
            html.H3("📘 Pollutant Info"),
            html.Ul([
                html.Li("CO – harmful to cardiovascular system"),
                html.Li("NO – contributes to smog"),
                html.Li("NO₂ – causes respiratory issues"),
                html.Li("O₃ – irritates lungs"),
                html.Li("SO₂ – causes breathing problems"),
                html.Li("PM2.5 – causes lung irritation"),
                html.Li("PM10 – affects respiratory system"),
                html.Li("NH₃ – eye/skin irritation"),
            ])
        ], className="left-panel"),

        html.Div([
            dcc.Graph(id='pollutant-graph', className='dash-graph')
        ], className="right-panel")
    ], className="flex-container"),

    html.Div("📈 Select Pollutant to View 5-Day Trend", style={
    'textAlign': 'center',
    'fontWeight': 'bold',
    'marginTop': '30px',
    'fontSize': '24px',
    'color': '#2c3e50'
}),


    dcc.Dropdown(
        id='pollutant-dropdown',
        options=[
            {'label': 'CO', 'value': 'co'},
            {'label': 'NO', 'value': 'no'},
            {'label': 'NO₂', 'value': 'no2'},
            {'label': 'O₃', 'value': 'o3'},
            {'label': 'SO₂', 'value': 'so2'},
            {'label': 'PM2.5', 'value': 'pm2_5'},
            {'label': 'PM10', 'value': 'pm10'},
            {'label': 'NH₃', 'value': 'nh3'}
        ],
        value='pm2_5',
        placeholder="Select a pollutant",
        className='pollutant-dropdown',
    clearable=False
    ),

    dcc.Graph(id='pollutant-history-graph'),

    # Latest air quality news section
    html.Div([
        html.H3("📰 Latest News on Air Quality"),
        html.Div(id='news-updates', children="Loading news..."),
    ], className="news-section")

])


def get_health_recommendation(aqi):
    if aqi == 1:
        return "Good – Air quality is satisfactory, and air pollution poses little or no risk."
    elif aqi == 2:
        return "Fair – Air quality is acceptable; however, some pollutants may slightly affect very sensitive individuals."
    elif aqi == 3:
        return "Moderate – Sensitive individuals should consider limiting prolonged outdoor exertion."
    elif aqi == 4:
        return "Poor – Everyone may begin to experience health effects; sensitive groups should avoid outdoor exertion."
    elif aqi == 5:
        return "Very Poor – Health warnings of emergency conditions. Everyone should avoid outdoor activity."
    else:
        return "Unknown AQI level. Please try again."


@app.callback(
    [Output('pollutant-graph', 'figure'),
     Output('aqi-display', 'children')],
    [Input('fetch-button', 'n_clicks'),
     Input('city-input', 'value')]
)
def update_graph(n_clicks, city):
    if city:
        aqi, pollutants = fetch_air_quality_data(API_KEY, city)
        if aqi is not None and pollutants is not None:
            df = process_pollutant_data(pollutants)
            values = df.iloc[0].values
            labels = df.columns

            colors = []
            for val in values:
                if val < 50:
                    colors.append('green')
                elif val < 100:
                    colors.append('orange')
                else:
                    colors.append('red')

            fig = go.Figure(data=[
                go.Bar(x=labels, y=values, marker_color=colors)
            ])

            fig.update_layout(
                title=f"Pollutant Levels in {city}",
                yaxis_title="Concentration (µg/m³)",
                xaxis_title="Pollutants"
            )

            aqi_display = f"AQI: {aqi} — {get_health_recommendation(aqi)}"
        else:
            fig = go.Figure()
            aqi_display = "Error fetching data. Please try again."
    else:
        fig = go.Figure()
        aqi_display = "Please enter a city name."

    return fig, aqi_display


@app.callback(
    Output('pollutant-history-graph', 'figure'),
    [Input('pollutant-dropdown', 'value'),
     Input('city-input', 'value')]
)
def update_pollutant_graph(pollutant, city):
    if not city or not pollutant:
        return go.Figure()

    data = fetch_historical_pollutant_data(API_KEY, city, pollutant)
    if data:
        dates = [d[0] for d in data]
        values = [d[1] for d in data]

        fig = go.Figure(data=[go.Scatter(x=dates, y=values, mode='lines+markers')])
        fig.update_layout(title=f"{pollutant.upper()} Levels in {city} (Last 5 Days)", xaxis_title="Date", yaxis_title="µg/m³")
        return fig
    else:
        return go.Figure()

# Function to fetch the latest news about air quality
@app.callback(
    Output('news-updates', 'children'),
    [Input('fetch-button', 'n_clicks')]
)
def update_news(n_clicks):
    if n_clicks > 0:
        news = fetch_air_quality_news(NEWS_API_KEY)
        if news:
            news_list = []
            for article in news:
                news_list.append(html.Div([
                    html.H3(article['title']),
                    html.P(article['description']),
                    html.A("Read more", href=article['url'], target="_blank")
                ], style={'margin-bottom': '20px'}))
            return news_list
        else:
            return "Error fetching news. Please try again."
    else:
        return "Please click the button to fetch news."


if __name__ == '__main__':
    app.run(debug=True)
