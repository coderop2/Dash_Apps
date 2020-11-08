import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

data = pd.read_csv("data.csv", parse_dates=['date'], usecols =[1,2,3,4,5,7,8,10,11,13,14,34,35,47])
data.drop(data[data['continent'].isnull()].index, inplace = True)
data.drop(data[(data['new_cases'].isnull()) & (data['total_cases'].isnull())].index, inplace = True)
groups = data.groupby('location')
x = groups.agg({'total_cases':'max'})[:10]
x.reset_index(inplace = True)
x.columns = ['Country', "Max Cases"]
x.sort_values("Max Cases",ascending = False, inplace = True)
x.reset_index(drop = True, inplace = True)
countries = data.location.unique()

fig = px.line(data, x="date", y="total_cases", color = "location")
fig.update_traces(mode='markers+lines')

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        COVID-19: A Country Wise Dashboard.
    '''),

    dcc.Graph(
        id='daily-count',
        figure=fig
    ),
    html.Div(
    html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in x.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(x.iloc[i][col]) for col in x.columns
            ]) for i in range(len(x))
        ])
    ]),
    
    dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in countries],
                value='Select the country'
            ),
    
    dcc.Graph(id='death-line-country-plot'))
])

@app.callback(Output('death-line-country-plot','figure'),[Input('xaxis-column','value')])
def updateScater(country):
    temp = data[data['location'] == country]
    fig2 = px.line(temp, x="date", y="total_deaths")
    fig2.update_traces(mode='markers+lines')
    return fig2

if __name__ == '__main__':
    app.run_server(debug=True)