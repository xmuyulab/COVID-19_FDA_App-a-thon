import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
import random
import json

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import click

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
colors = dict(background = '#111111', text = '#7FDBFF')
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)






CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--input_path', '-i', required=True, type=click.Path(), help='Input data path')
@click.option('--port', '-p', default=8050, type=int, help='Port')


def tcrmap(input_path, port):
    
    df_init = pd.read_csv(input_path,sep = '\t')
    df = df_init.copy()


    sample = df_init['sample'].unique().tolist()

    app.layout = html.Div(id = 'page',children=[

        #Title
        html.H1(
            children='TCR Map',
            style = dict(textAlign = 'center', color = colors['text'],backgroundColor = colors['background'])),

        #2 input blocks
        html.Div([
            #Sample selecter
            html.Div([

                #title
                html.H2(
                    children='Sample Selector:',
                    style = dict(textAlign = 'center', color = colors['text'],backgroundColor = colors['background'])),
                #group or individual
                html.H6('group-or-individual'),
                html.Div([
                    dcc.RadioItems(
                        id='group-or-individual',
                        options=[
                            {'label': 'Patient Group', 'value': 'group'},
                            {'label': 'Individual Patient', 'value': 'individual'}
                        ],
                        value = 'group',
                        labelStyle={'display': 'inline-block','textAlign' :'left'}
                    )
                ]),

    #             html.H6('If group'),
                #condition
                html.Div([
                    html.Div(className='app-controls-name',
                                                     children='Condition:'),
                    dcc.Dropdown(
                        id='condition',
                        options=[{'label': i, 'value': i} for i in ['Health', 'CMV','COVID19']],
    #                     value = 'all',
                        multi=True,
                        style={ 'width': '80%'}
                    )
                ]),

                #Age
                html.Div([

                    html.Div(children='Age:'),
                    html.Div([
                        dcc.RangeSlider(
                            id='age-range',
                            min=0,
                            max=90,
                            step=1,
                            value=[40, 45],
                            marks={str(age): str(age) for age in [0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90]},
    #                         marks={
    #                             30:'30',
    #                             40:'40',
    #                             50:'50',
    #                             60:'60',
    #                             70:'70',
    #                             80:'80'
    #                         }

                        ),
                    ]),
                ]),

    #             html.H6('If Individual'),
                html.Div([

                    html.Div("Individual Patient"),     
                    dcc.Dropdown(
                        id='sample',
                        options=[{'label': i, 'value': i} for i in sample],
                        multi=True,
                        style={ 'width': '80%'}


                    ),])  


            ],style={'display': 'inline-block', 'width': '48%','padding': '5px 10px'}     
            ),#Sample Selector


            #Color Legend
            html.Div([

                html.H2(
                    children='Color Legend:',
                    style = dict(textAlign = 'center', color = colors['text'],backgroundColor = colors['background'])),

                #or
                html.H6('Density or Diff Density map'),
                html.Div([
                    dcc.RadioItems(
                        id='density-or-diff-density',
                        options=[
                            {'label': 'Density map', 'value': 'Density'},
                            {'label': 'Diff Density map', 'value': 'Diff-Density'},
                            {'label': 'Condition', 'value': 'condition'}
                        ],
                        value = 'Density',
                        labelStyle={'display': 'inline-block','textAlign' :'left'}
                    )
                ]),

                #Density map
                html.Div([
                    html.H6("Density map"),
                    html.Div([

                        dcc.Dropdown(
                            id='density-map',
                            options=[{'label': i, 'value': i} for i in ['Health', 'CMV','COVID19']],
                            value='Health',

                        )     
                    ],style={'display': 'inline-block', 'width': '80%'}),
                ]),

                #Diff Density map
                html.Div([
                    html.H6("Diff Density map"),
                    html.Div([

                        dcc.Dropdown(
                            id='diff-density-map1',
                            options=[{'label': i, 'value': i} for i in ['Health', 'CMV','COVID19']],
                            value='COVID19',
                            style={'width': '90%'}
                        ),  
                        html.Div(
                            children="——",
                            style = {'width': '20%','textAlign' : 'left'}
                        ),
                        dcc.Dropdown(
                            id='diff-density-map2',
                            options=[{'label': i, 'value': i} for i in ['Health', 'CMV','COVID19']],
                            value='Health',
                            style={'width': '90%'}
                        ) 
                    ],style={'textAlign':'center', 'width': '80%','justify-content': 'space-between','display':'flex'}),
                ]),




           ],style={'display': 'inline-block', 'width': '48%','padding': '5px 10px'}),
           #Color Legend 
        ],
        style={'width': '100%',
                    'padding': '10px 5px','justify-content': 'space-between','display':'flex'}),#2 input



        #2 output
        html.Div([

            #figure
            html.Div([
                html.H6("TCR MAP"),
                dcc.Graph(
                    id='graphic',
                        #hoverData={'points': [{'customdata': 'Japan'}]}
                ),
            ],
            style={'display': 'inline-block', 'width': '50%','padding': '5px 10px','backgroundColor': 'rgb(250, 250, 250)'}), 

            #information
            html.Div([
                html.H6("Information of Selected TCR"),
                html.Div(className='row', children=[
                    html.Div([
                        dcc.Markdown("""
                    **Click Data**

                    Click on points in the graph.
                    """),
    #                 html.Pre(id='hover_data', style=styles['pre'])
                        html.Div(
                            id = 'click-data',
                        )
                ],)

    #             html.Div([
    #                 dcc.Markdown("""
    #                     **Click Data**

    #                     Click on points in the graph.
    #                 """),
    #                 html.Pre(id='click-data', style=styles['pre']),
    #             ], className='three columns'),

            ])
            ],
            style={'display': 'inline-block', 'width': '45%'}), 
            ],style={'justify-content': 'space-between','display':'flex'}),

    ],style={'borderBottom': 'thin lightgrey solid',
            'backgroundColor': 'rgb(250, 250, 250)',})

    trace_layout = go.Layout(
        # plot_bgcolor='red',  # 图背景颜色
        paper_bgcolor='white',  # 图像背景颜色
        autosize=True,
        # width=2000,
        # height=1200,
    #     title='数据密度热力图',
        titlefont=dict(size=30, color='gray'),
        showlegend = True,
        # 图例相对于左下角的位置
        legend=dict(
            x=0.02,
            y=0.02
        ),

        # x轴的刻度和标签
        xaxis=dict(title='x',  # 设置坐标轴的标签
                   titlefont=dict(color='red', size=14),
                   tickfont=dict(color='blue', size=14, ),
                   tickangle=0,  # 刻度旋转的角度
                   showticklabels=True,  # 是否显示坐标轴
                   # 刻度的范围及刻度
                   # autorange=False,
                   # range=[0, 100],
                   # type='linear',
                   ),

        # y轴的刻度和标签
        yaxis=dict(title='y',  # 坐标轴的标签
                   titlefont=dict(color='blue', size=14),  # 坐标轴标签的字体及颜色
                   tickfont=dict(color='green', size=14, ),  # 刻度的字体大小及颜色
                   showticklabels=True,  # 设置是否显示刻度
                   tickangle=0,
                   # 设置刻度的范围及刻度
                   autorange=True,
                   # range=[0, 100],
                   # type='linear',
                   ),
    )



    def get_group_dataframe(df,conditions,age_range):
        #group patient selected
        if conditions==None or len(conditions)==0:
            dataframe = df
        else:
            dataframe = pd.DataFrame()
            for condition in conditions:
                dataframe = pd.concat([dataframe,df[df['label']==condition]], axis=0)
        data_selected = dataframe[dataframe['Age']>age_range[0]]
        data_selected = dataframe[dataframe['Age']<age_range[1]]
        return data_selected

    def get_individual_datafram(df,samples):
         #individual patient selected
        if samples == None or len(samples)==0:
            dataframe=df
        else:
            df_selected = pd.DataFrame()
            for sample in samples:
                df_selected =  pd.concat([df_selected,df[df['sample']==sample]], axis=0) 
            dataframe=df_selected
        return dataframe

    def get_kernel(df,dodd,density_map):
        #拟合函数选择
        if dodd == "condition":
            nData = np.array([df['X'], df['Y']])
        else:
            nData = np.array([df['X'][df.label==density_map], df['Y'][df.label==density_map]])

        kernel = stats.gaussian_kde(nData)
        return kernel

    def normalize(Z):
        Znor=(Z-min(Z))/(max(Z)-min(Z))
        #sum_all = sum(Znor)
        #Znor = Znor / sum_all
        return Znor

    def get_scatter_data(df,kernel):
        #计算df对应的‘Z’
        nOriData = np.array([df['X'], df['Y']])   
        Z = kernel(nOriData)   
        Znor = normalize(Z)  
        df_res = df.copy()
        df_res['Z'] = Znor
        return df_res

    def get_diff_data(df,kernel_1,kernel_2):
        data1 = get_scatter_data(df,kernel_1)
        data2 = get_scatter_data(df,kernel_2)
        diff_data = data1.copy()
        diff_data['Z'] = data1['Z']-data2['Z']
        return diff_data

    def fig_show(dataframe,dodd):

        color = dict(CMV = 'purp', Health = 'greens',COVID19 = 'redor')
        color_label = dict(Health='yellowgreen',CMV = 'brown',COVID19 = 'red')
        df_Heal = dataframe[dataframe.label=='Health']
        df_CMV = dataframe[dataframe.label=='CMV']
        df_COVID19 = dataframe[dataframe.label=='COVID19']

        if dodd=='condition':

            trace1 = go.Scatter(x= df_Heal["X"],y=df_Heal["Y"],mode='markers',
                         name = 'Health',
                         customdata=df_Heal,
                         text=df_Heal["Z"],#设置数值标签的值
                            marker=dict(
                            color = color_label['Health'],
                             opacity = 0.7,))
            trace2 = go.Scatter(x= df_CMV["X"],y=df_CMV["Y"],mode='markers',
                                name = 'CMV',
                                customdata=df_CMV,
                                text=df_CMV["Z"],#设置数值标签的值
                                marker=dict(
                                color = color_label['CMV'],
                                 opacity = 0.7,))
            trace3 = go.Scatter(x= df_COVID19["X"],y=df_COVID19["Y"],mode='markers',
                                name = 'COVID19',
                                customdata=df_COVID19,
                                text=df_COVID19["Z"],#设置数值标签的值
                                marker=dict(
                                color = color_label['COVID19'],
                                 opacity = 0.7,))
        else:
            trace1 = go.Scatter(x= df_Heal["X"],y=df_Heal["Y"],mode='markers',
                             name = 'Health',
                             customdata=df_Heal,
                             text=df_Heal["Z"],#设置数值标签的值
                                marker=dict(
                                color = np.array(df_Heal["Z"]),
                                    showscale=True,
    #                          colorscale=color['Health'],
                                 opacity = 0.7,))
            trace2 = go.Scatter(x= df_CMV["X"],y=df_CMV["Y"],mode='markers',
                                name = 'CMV',
                                customdata=df_CMV,
                                text=df_CMV["Z"],#设置数值标签的值
                                marker=dict(
                                color = np.array(df_CMV["Z"]),
                                    showscale=True,
    #                          colorscale=color['CMV'],
                                 opacity = 0.7,))
            trace3 = go.Scatter(x= df_COVID19["X"],y=df_COVID19["Y"],mode='markers',
                                name = 'COVID19',
                                customdata=df_COVID19,
                                text=df_COVID19["Z"],#设置数值标签的值
                                marker=dict(
                                color = np.array(df_COVID19["Z"]),
                                    showscale=True,
    #                          colorscale=color['COVID19'],
                                 opacity = 0.7,))

        data = [trace1,trace2,trace3]

        fig = go.Figure(data=data,layout=trace_layout)
        fig.update_layout(title="Your data", xaxis_title="X", yaxis_title="Y")
        #fig.add_trace(trace1)
        return fig

    @app.callback(
         Output('graphic', 'figure'),
        [Input('group-or-individual', 'value'),
         Input('condition', 'value'),
         Input('age-range', 'value'),
         Input('sample', 'value'),
         Input('density-or-diff-density', 'value'),
         Input('density-map', 'value'),
         Input('diff-density-map1', 'value'),
         Input('diff-density-map2', 'value'),
         ]
    )
    def update_graph(goi,conditions,age_range,samples,dodd,dm,ddm1,ddm2):
        if goi=='group':
            selected_data=get_group_dataframe(df,conditions,age_range)
        else:
            selected_data=get_individual_datafram(df,samples)
        if dodd=='condition':
            kernel=get_kernel(df,dodd,dm)
            point_dataframe=get_scatter_data(selected_data,kernel)
        elif dodd=='Density':
            kernel=get_kernel(df,dodd,dm)
            point_dataframe=get_scatter_data(selected_data,kernel)
        else:
            kernel_1=get_kernel(df,dodd,ddm1)
            kernel_2=get_kernel(df,dodd,ddm2)
            point_dataframe=get_diff_data(selected_data,kernel_1,kernel_2)
    #     print(point_dataframe)

        fig=fig_show(point_dataframe,dodd)

        return fig


    @app.callback(
        Output('click-data', 'children'),
        Input('graphic', 'clickData'))
    def display_click_data(clickData):

        attr = [col for col in df.columns]+['estimated density']
        attr[0]='index'
        hd = clickData
        if hd==None:
            hov_df=pd.DataFrame({ "attribute":attr})
        else:
            value = hd['points'][0]['customdata']
            hov_df = pd.DataFrame({
                "attribute":attr,
                "valve":value
            })
        return html.Table([
            html.Thead(
                html.Tr([html.Th(col) for col in hov_df.columns])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(hov_df.iloc[i][col]) for col in hov_df.columns
                ]) for i in range(len(hov_df))
            ])
        ])


    @app.callback(
        [Output('condition', 'disabled'),
         Output('condition', 'placeholder'),
        Output('age-range', 'disabled'),
        Output('sample', 'disabled'),
        Output('sample', 'placeholder'),],
        Input('group-or-individual', 'value'))
    def button_interacr_left(goi):
        able= 'Select...'
        disable = 'Disabled'
        if goi=='group':

            return False,able,False,True,disable
        else:
            return True,disable,True,False,able

    @app.callback(
        [Output('density-map', 'disabled'),

        Output('diff-density-map1', 'disabled'),

        Output('diff-density-map2', 'disabled'),],
        Input('density-or-diff-density', 'value'))
    def button_interacr_right(dodd):
        if dodd=='Density':

            return False,True,True
        elif dodd=='Diff-Density':
            return True,False,False
        else:
            return True,True,True

    app.run_server(debug=True, use_reloader=False, host='0.0.0.0', port=port)

if __name__ == '__main__':
    tcrmap()

