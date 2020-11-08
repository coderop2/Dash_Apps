import dash
import dash_table
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

x = groups.agg({'total_cases':'max'})
x.reset_index(inplace = True)
x.columns = ['Country', "Max Cases"]
x.sort_values("Max Cases",ascending = False, inplace = True)
x.reset_index(drop = True, inplace = True)

top_ten = x[:10]

countries = data.location.unique()

fig = px.line(data, x="date", y="total_cases", color = "location")
fig.update_traces(mode='markers+lines')

app.layout = html.Div(children=[
    html.H1(children='COVID DashBoard'),

    html.Div(children='''
        COVID-19: A Country Wise Dashboard.
    '''),
    dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in countries],
                placeholder="Select a city",
                value='India'
            ),
    
    html.Div([
        html.Div([dash_table.DataTable(
        id='top-ten',
        columns=[{"name": i, "id": i} for i in top_ten.columns],
        data=top_ten.to_dict('records'))
                 ],style={'width': '20%', 'display': 'inline-block'}),
        
        html.Div([
              dcc.Graph(
              id='daily-count',
              figure=fig)
        ],style={'width': '80%', 'display': 'inline-block', 'float': 'right'}),
    ]),
    
    html.Div([
        html.Div([dcc.Graph(id='total-cases-country-plot')]
    ,style={'width': '32%', 'display': 'inline-block'}),
        
    html.Div([dcc.Graph(id='new-cases-country-plot')]
    ,style={'width': '32%', 'display': 'inline-block'}),
    
    html.Div([
    dcc.Graph(id='death-line-country-plot')],style={'width': '32%', 'display': 'inline-block'})])
])

@app.callback(
    Output('total-cases-country-plot','figure'),
    [Input('xaxis-column','value')])
def updateTotalCountPlot(country):
    temp = data[data['location'] == country]
    fig2 = px.line(temp, x="date", y="total_cases")
    fig2.update_traces(mode='markers+lines')
    return fig2

@app.callback(
    Output('death-line-country-plot','figure'),
    [Input('xaxis-column','value')])
def updateDeathPlot(country):
    temp = data[data['location'] == country]
    fig2 = px.line(temp, x="date", y="total_deaths")
    fig2.update_traces(mode='markers+lines')
    return fig2

@app.callback(
    Output('new-cases-country-plot','figure'),
    [Input('xaxis-column','value')])
def updateNewCasesPlot(country):
    temp = data[data['location'] == country]
    fig2 = px.line(temp, x="date", y="new_deaths")
    fig2.update_traces(mode='markers+lines')
    return fig2

if __name__ == '__main__':
    app.run_server(debug=True)