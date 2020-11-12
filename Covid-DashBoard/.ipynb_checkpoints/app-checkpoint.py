import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

colors = {
    'background': '#2D2D2D',
    'text': '#E1E2E5',
    'figure_text': '#ffffff',
    'confirmed_text':'#3CA4FF',
    'deaths_text':'#f44336',
    'recovered_text':'#5A9E6F',
    'highest_case_bg':'#393939',
    'linecolor' : '#545454', 
    'gridcolor': '#363636'
}

divBorderStyle = {
    'backgroundColor' : '#393939',
    'borderRadius': '12px',
   
}

#Creating custom style for local use
boxBorderStyle = {
    'borderColor' : '#393939',
    'borderStyle': 'solid',
    'borderRadius': '10px',
    'borderWidth':2,
}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

data = pd.read_csv("data.csv", parse_dates=['date'], usecols =[1,2,3,4,5,7,8,10,11,13,14,34,35,47])
data.drop(data[data['continent'].isnull()].index, inplace = True)
data.drop(data[(data['new_cases'].isnull()) & (data['total_cases'].isnull())].index, inplace = True)

groups = data.groupby('location')

df_pop = groups.agg({'population':'max','total_cases':'max','total_deaths':'max'})
x = df_pop[['total_cases','total_deaths']]

x.reset_index(inplace = True)
x.columns = ['Country', "Total Cases", "Total Deaths"]
x.sort_values("Total Cases",ascending = False, inplace = True)
x.reset_index(drop = True, inplace = True)

top_ten = x[:10]

countries = data.location.unique()
ten_count = top_ten.Country

def getMainPlot():
    fig = px.line(data.query("location in @ten_count"), x="date", y="total_cases", color = "location", height=400, width=1100)
    fig.update_traces(mode='markers+lines')
    fig.update_xaxes(showgrid=True, gridwidth=2, gridcolor='#363636')
    fig.update_yaxes(showgrid=True, gridwidth=2, gridcolor='#363636')
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ),
            font=dict(
                family="Courier New, monospace",
                size=14,
                color=colors['figure_text'],
            ),
            paper_bgcolor=colors['background'],
            plot_bgcolor=colors['background'],
            margin=dict(l=0, 
                        r=0, 
                        t=0, 
                        b=0
                        ))
    return fig

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(children='COVID DashBoard',style={'textAlign': 'center','color': colors['text']}),
    html.Div([
                html.Div([html.H4("Total Cases : ",
                                 style={'textAlign':"center",
                                       'color': colors['confirmed_text']}),

                         html.P(f"{int(x['Total Cases'].sum()):,d}", 
                               style={'textAlign':'center',
                                     'font':30,
                                     'color': colors['confirmed_text']}),

                         html.P(f"Increase in total cases in the past 24 Hrs : {int(data[data['date'] == '2020-11-02'].new_cases.sum()):,d} "+"("+str(round(int(data[data['date'] == '2020-11-02'].new_cases.sum())/int(x['Total Cases'].sum())*100, 3))+"%)",
                               style={'textAlign':'center',
                                     'color': colors['confirmed_text']
                                     })
                         ],style=divBorderStyle,className='four columns'),


                 html.Div([html.H4("Total Deaths : ",
                                 style={'textAlign':"center",
                                       'color': colors['deaths_text']}),

                         html.P(f"{int(x['Total Deaths'].sum()):,d}", 
                               style={'textAlign':'center',
                                     'font':30,
                                     'color': colors['deaths_text']}),

                         html.P(f"Increase in total deaths in the past 24 Hrs : {int(data[data['date'] == '2020-11-02'].new_deaths.sum()):,d} "+"("+str(round(int(data[data['date'] == '2020-11-02'].new_deaths.sum())/int(x['Total Cases'].sum())*100, 3))+"%)",
                               style={'textAlign':'center',
                                     'color': colors['deaths_text']
                                     })
                         ],style=divBorderStyle,className='four columns'),
        
                html.Div([
                        html.H6(children='Total Cases Per Million: ',
                               style={
                                   'textAlign': 'center',
                                   'color': colors['recovered_text'],
                               }
                               ),
                        html.P("%8.2f"%(round((df_pop.total_cases.sum()/df_pop.population.sum())*1000000,2)),
                               style={
                            'textAlign': 'center',
                            'color': colors['recovered_text'],
                            'fontSize': 20,
                        }),
                        html.H6(children='Total Deaths Per Million: ',
                               style={
                                   'textAlign': 'center',
                                   'color': colors['deaths_text'],
                               }
                               ),
                        html.P("%8.2f"%(round((df_pop.total_deaths.sum()/df_pop.population.sum())*1000000,2)),
                               style={
                            'textAlign': 'center',
                            'color': colors['deaths_text'],
                            'fontSize': 20,
                        })
                        ],style=divBorderStyle,className='four columns')
    ]),
       
    html.Div([
        html.Div([dash_table.DataTable(
                                    id='countries',
                                    columns=[{"name": i, "id": i, "deletable": False, "selectable": True} for i in x.columns],
                                    fixed_rows={'headers': True, 'data': 0},
                                    data=x.to_dict('records'),
                                    sort_action='native',
                                    filter_action='native',
                                    row_selectable='single',
                                    
                                    style_header={
                                                  'backgroundColor': 'rgb(30, 30, 30)',
                                                  'fontWeight': 'bold'
                                                  },
                                    style_cell={
                                                'backgroundColor': 'rgb(100, 100, 100)',
                                                'color': colors['text'],
                                                'maxWidth': 0,
                                                'fontSize':14},
                                    style_table={
                                                 'maxHeight': '350px',
                                                 'overflowY': 'auto'
                                                },
                                    style_data={
                                                'whiteSpace': 'normal',
                                                'height': 'auto',
                                                })],
                 style={'width': '25%', 'display': 'inline-block','padding-top': '30px','padding-left': '10px'}),
        
        html.Div([
              dcc.Graph(
              id='daily-count',
              figure=getMainPlot())
        ],style={'width': '70%', 'display': 'inline-block', 'float': 'right','padding-top': '30px','padding-right': '30px'}),
    ]),
    html.Div([
              html.Span(
                       style={'color': colors['text']},
                       id='my-country'),
              html.Span(
                        style={'color': colors['confirmed_text'],
                        'fontWeight': 'bold'},
                        id='my-confirmed'),
              html.Span(" with deaths: ",
                       style={'color': colors['text']}),
              html.Span(
                        style={'color': colors['deaths_text'],
                        'fontWeight': 'bold'},
                        id='my-deaths')
             ], style={'padding-top': '20px'}),
    
    html.Div([
        html.Div([dcc.Graph(id='total-cases-country-plot')]
        ,style={'width': '30%', 'display': 'inline-block', 'padding-left':'35px'}),
        
    html.Div([dcc.Graph(id='new-cases-country-plot')]
        ,style={'width': '30%', 'display': 'inline-block', 'padding-left':'35px'}),
    
    html.Div([dcc.Graph(id='death-line-country-plot')]
        ,style={'width': '30%', 'display': 'inline-block', 'padding-left':'35px'})], style={'padding-top': '20px'})
])



@app.callback(
    [Output('my-country', component_property = 'children'),
     Output('my-confirmed', component_property = 'children'),
    Output('my-deaths', component_property = 'children')],
    [Input('countries', 'selected_rows')])
def getCountrySpecificData(selected_rows):
    value = ""
    if selected_rows is not None:
        value = x.loc[selected_rows[0]].Country
    else:
        value = x.loc[0].Country
    temp = data[data['location'] == str(value)]
    
    return str(value), str(temp.total_cases.max()), str(temp.total_deaths.max())

@app.callback(
    [Output('total-cases-country-plot','figure'),
    Output('death-line-country-plot','figure'),
    Output('new-cases-country-plot','figure')],
    [Input('countries','selected_rows')])
def plotCountrySpecificData(selected_rows):
    country = ""
    if selected_rows is not None:
        country = x.loc[selected_rows[0]].Country
    else:
        country = x.loc[0].Country
    
    temp = data[data['location'] == country]
    
    plots = []
    
    for col, color in zip(['total_cases','total_deaths','new_cases'],['#3CA4FF','#BB2205','#2d6187']):
        pxfig = px.line(temp, x='date', y=col, color_discrete_sequence = [color])
        pxfig.update_xaxes(showgrid=True, gridwidth=2, gridcolor=colors['gridcolor'])
        pxfig.update_yaxes(showgrid=True, gridwidth=2, gridcolor=colors['gridcolor'])
        pxfig.update_layout(xaxis_title = None,
                            yaxis_title = None,
                            title={'text': col.replace("_"," ").upper(),
                                   'y':0.9,
                                   'x':0.5,
                                   'xanchor': 'center',
                                   'yanchor': 'top'},
                           font=dict(family="Courier New, monospace",
                                     size=14,
                                     color=colors['figure_text']),
                           paper_bgcolor=colors['background'],
                           plot_bgcolor=colors['background'],
                           margin=dict(l=0, r=0, t=0, b=0))
        pxfig.update_traces(mode='markers+lines')
        plots.append(pxfig)
    
    return plots[0], plots[1], plots[2]


if __name__ == '__main__':
    app.run_server(debug=True)