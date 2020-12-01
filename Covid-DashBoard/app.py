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
    # 'margin-left': '15px',
    # 'margin-right': '15px',
    # 'height': '135px',
    # 'width':'465px',
    'textAlign':'center'
}

#Creating custom style for local use
boxBorderStyle = {'borderColor' : '#393939',
                  'borderStyle': 'solid',
                  'borderRadius': '10px',
                  'borderWidth':2,
                  'width': '15%',
                  'text-align' : 'center',
                  'margin-left' : '17.5%',
                  'margin-right' : '17.5%'
                                 }

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

data = pd.read_csv("data.csv", parse_dates=['date'], usecols =[1,2,3,4,5,7,8,10,11,13,14,34,35,47])
data.drop(data[data['continent'].isnull()].index, inplace = True)
data.drop(data[(data['new_cases'].isnull()) & (data['total_cases'].isnull())].index, inplace = True)

groups = data.groupby('location')

df_pop = groups.agg({'population':'max','total_cases':'max','total_deaths':'max'})
temp_df_pop = df_pop.reset_index()

x = df_pop[['total_cases','total_deaths']]

x.reset_index(inplace = True)
x.columns = ['Country', "Total Cases", "Total Deaths"]
x.sort_values("Total Cases",ascending = False, inplace = True)
x.reset_index(drop = True, inplace = True)

top_ten = x[:10]

countries = data.location.unique()
ten_count = top_ten.Country
selected_country = x.loc[0].Country

def getMainPlot():
    fig = px.line(data.query("location in @ten_count"), x="date", y="total_cases", color = "location", color_discrete_sequence =["#e3f2fd","#bbdefb","#90caf9","#64b5f6","#42a5f5",'#2196f3','#1e88e5','#1976d2','#1565c0','#0d47a1'])#, height=400, width=1100)
    # fig.update_traces(mode='markers+lines')
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
    html.H1(children='COVID DashBoard',style={'textAlign': 'center','color': colors['text']}, className = 'row'),
    html.Div([
                html.Div([html.H4("Worldwide Total Cases : ",
                                 style={'color': colors['confirmed_text']}),

                         html.P(f"{int(x['Total Cases'].sum()):,d}", 
                               style={'font':30,
                                     'color': colors['confirmed_text']}),

                         html.P(f"Increase in total cases in the past 24 Hrs : {int(data[data['date'] == '2020-11-02'].new_cases.sum()):,d} "+"("+str(round(int(data[data['date'] == '2020-11-02'].new_cases.sum())/int(x['Total Cases'].sum())*100, 3))+"%)",
                               style={'color': colors['confirmed_text']})
                         ],style=divBorderStyle,className='four columns'),


                 html.Div([html.H4("Worldwide Total Deaths : ",
                                 style={'color': colors['deaths_text']}),

                         html.P(f"{int(x['Total Deaths'].sum()):,d}", 
                               style={'font':30,
                                     'color': colors['deaths_text']}),

                         html.P(f"Increase in total deaths in the past 24 Hrs : {int(data[data['date'] == '2020-11-02'].new_deaths.sum()):,d} "+"("+str(round(int(data[data['date'] == '2020-11-02'].new_deaths.sum())/int(x['Total Cases'].sum())*100, 3))+"%)",
                               style={'color': colors['deaths_text']
                                     })
                         ],style=divBorderStyle,className='four columns'),
        
                html.Div([
                        html.H6(children='Total Cases Per Million : ' + 
                                "%8.2f"%(round((df_pop.total_cases.sum()/df_pop.population.sum())*1000000,2)),
                               style={'color': colors['confirmed_text'],
                                   'margin-top': '20px',
                                   'margin-bottom':'20px'}
                               ),
                        html.H6(children='Total Deaths Per Million : ' + 
                                "%8.2f"%(round((df_pop.total_deaths.sum()/df_pop.population.sum())*1000000,2)),
                               style={'color': colors['deaths_text'],
                                   'margin-top': '20px',
                                   'margin-bottom':'20px'
                               })
                        ],style=divBorderStyle,className='four columns')
    ], className = 'row'),
       
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
                                                 'maxHeight': '400px',
                                                 'overflow-y': 'auto'
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
        ],style={'width': '70%', 'display': 'inline-block', 'float': 'right'}),
    ], className = 'row', style = {'margin-top': '2%'}),
    
    # html.Div([
    #           html.Span(
    #                    style={'color': colors['text']},
    #                    id='my-country'),
    #           html.Span(
    #                     style={'color': colors['confirmed_text'],
    #                     'fontWeight': 'bold'},
    #                     id='my-confirmed'),
    #           html.Span("<br>",
    #                     id='testing'),
    #           html.Span(" with deaths: ",
    #                    style={'color': colors['text']}),
    #           html.Span(
    #                     style={'color': colors['deaths_text'],
    #                     'fontWeight': 'bold'},
    #                     id='my-deaths')
    #          ], style={'padding-top': '20px'}, className = 'row'),
    
    html.Div([html.H2(id = 'countryHeader')], 
             id = 'countryName', 
             style={'font-family':'Courier New, monospace', 
                    'text-align':'center',
                    'color' : colors['figure_text']
                   }, className = 'row'),
    
    html.Div([
                html.Div([html.H6("Cases : ",
                                 style={'color': colors['confirmed_text']}),
                          html.Div([
                                html.P([
                                    html.Span("Total Cases : ", style = {'color':colors['figure_text']}),
                                    html.Span(id = 'country_cases', style = {'color' : 'lightblue'}),
                                    html.Span(id = 'country_prev_day_cases', style = {'color' : 'blue'})
                                ], style = {'text-align':'center'}),
                                html.P([
                                    html.Span("Cases Per Million : ", style = {'color':colors['figure_text']}),
                                    html.Span(id = 'country_per_million_cases', style = {'color' : 'lightblue'})
                                ], style = {'text-align':'center'})
                            ])
                         ],style=boxBorderStyle, className='two columns'),


                 html.Div([html.H6("Deaths : ",
                                 style={'color': colors['deaths_text']}),
                           html.Div([
                                html.P([
                                    html.Span("Total Deaths : ", style = {'color':colors['figure_text']}),
                                    html.Span(id = 'country_deaths', style = {'color' : 'orange'}),
                                    html.Span(id = 'country_prev_day_deaths', style = {'color' : 'red'})
                                ], style = {'text-align':'center'}),
                                html.P([
                                    html.Span("Deaths Per Million : ", style = {'color':colors['figure_text']}),
                                    html.Span(id = 'country_per_million_deaths', style = {'color' : 'red'})
                                ], style = {'text-align':'center'})
                            ])
                         ],style=boxBorderStyle, className='two columns')
    ], className = 'row'),
    
    html.Div([
        html.Div([dcc.RadioItems(
                    options = [{'label': 'Line Plot', 'value': 'line'},
                               {'label': 'Bar Plot', 'value': 'bar'}],
                    value = 'line',
                    labelStyle={'display': 'inline-block', 'color':colors['figure_text']},
                    id = 'totalCases_radio')
                  ,dcc.Graph(id='total-cases-country-plot')], 
                 className = 'eachCountry',style={'width': '30%','display': 'inline-block', 'margin-left':'2%'}),
        
        html.Div([dcc.RadioItems(
                    options = [{'label': 'Line Plot', 'value': 'line'},
                               {'label': 'Bar Plot', 'value': 'bar'}],
                    value = 'line',
                    labelStyle={'display': 'inline-block', 'color':colors['figure_text']},
                    id = 'newCases_radio')
                  ,dcc.Graph(id='new-cases-country-plot')], 
                 className = 'eachCountry',style={'width': '30%','display': 'inline-block', 'margin-left':'3%', 'margin-right':'3%'}),
        
        html.Div([dcc.RadioItems(
                    options = [{'label': 'Line Plot', 'value': 'line'},
                               {'label': 'Bar Plot', 'value': 'bar'}],
                    value = 'line',
                    labelStyle={'display': 'inline-block', 'color':colors['figure_text']},
                    id = 'totalDeaths_radio')
                  ,dcc.Graph(id='death-line-country-plot')], 
                 className = 'eachCountry',style={'width': '30%','display': 'inline-block', 'margin-right':'2%'})] 
        , className = 'row', style = {'margin-top': '2%'})
], className = 'all_cols')

@app.callback(
    [Output('country_cases', component_property = 'children'),
     Output('country_prev_day_cases', component_property = 'children'),
     Output('country_per_million_cases', component_property = 'children'),
     Output('country_deaths', component_property = 'children'),
     Output('country_prev_day_deaths', component_property = 'children'),
     Output('country_per_million_deaths', component_property = 'children'),
     Output('countryHeader', component_property = 'children')],
    [Input('countries', 'selected_rows')])
def getGetCountrySpecificInfo(selected_country, death = False):
    country = x.loc[0].Country
    if selected_country is not None:
        country = x.loc[selected_country[0]].Country
    country_group = groups.get_group(country)

    temp = x[x['Country'] == country]
    prev_day = country_group[country_group['date'] == '11-02-2020']

    obj1 = str(temp['Total Cases'].values[0])
    obj2 = "+" + str(prev_day['new_cases'].values[0])
    obj3 = "%8.2f"%(round((temp['Total Cases'].values[0]/country_group.population.values[0])*1000000,2))
    obj4 = str(temp['Total Deaths'].values[0])
    obj5 = "+" + str(prev_day['new_deaths'].values[0])
    obj6 = "%8.2f"%(round((temp['Total Deaths'].values[0]/country_group.population.values[0])*1000000,2))
    return obj1, obj2, obj3, obj4, obj5, obj6, str(country)
# @app.callback(
#     [Output('my-country', component_property = 'children'),
#      Output('my-confirmed', component_property = 'children'),
#     Output('my-deaths', component_property = 'children'),
#     Output('countryHeader', component_property = 'children')],
#     [Input('countries', 'selected_rows')])
# def getCountrySpecificData(selected_rows):
#     country = x.loc[0].Country
#     if selected_rows is not None:
#         country = x.loc[selected_rows[0]].Country
#     else:
#         country = x.loc[0].Country
#     temp = data[data['location'] == str(country)]
    
#     return str(country), str(temp.total_cases.max()), str(temp.total_deaths.max()), str(country)

@app.callback(
    [Output('total-cases-country-plot','figure'),
    Output('new-cases-country-plot','figure'),
    Output('death-line-country-plot','figure')],
    [Input('countries','selected_rows'),
    Input('totalCases_radio', 'value'),
    Input('newCases_radio', 'value'),
    Input('totalDeaths_radio', 'value')])
def plotCountrySpecificData(selected_rows, *values):
    country = x.loc[0].Country
    if selected_rows is not None:
        country = x.loc[selected_rows[0]].Country
    
    temp = data[data['location'] == country]
    selected_country = country
    
    plots = []
    
    for col, color, value in zip(['total_cases','new_cases','total_deaths'],['#3CA4FF','#2d6187','#BB2205'], values):
        if value == "bar":
            pxfig = px.bar(temp, x='date', y=col, color_discrete_sequence = [color])
        else:
            pxfig = px.line(temp, x='date', y=col, color_discrete_sequence = [color])
            pxfig.update_traces(mode='markers+lines')
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
        plots.append(pxfig)
    
    return plots[0], plots[1], plots[2]


if __name__ == '__main__':
    app.run_server(debug=True)