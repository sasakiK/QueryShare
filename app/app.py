import os
import io
import sys
import dash
import MeCab
import base64
import neologdn
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

from dash.dependencies import Input, Output, State

from flask import send_from_directory


app = dash.Dash()
app.title = 'Training OPT'
# app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
app.config.suppress_callback_exceptions = True

# --------------------------- preprocessing ---------------------------

# load objects or other (To use it, like "processing.objname")
import processing


# --------------------------- define function -------------------------


# --------------------------- app_layout ---------------------------


# define resusable components ------------------------

# define title components (reusable components)
title_components = html.Div([

    # load local css
    # ------------- style -------------
    html.Link(rel='stylesheet', href='/static/sty.css'),
    html.Link(rel='stylesheet', href='/static/animate.css'),
    # ------------- font-family -------------
    html.Link(rel='stylesheet', href='/static/montserrat.css'),
    html.Link(rel='stylesheet', href='/static/notosans.css'),
    html.Link(rel='stylesheet', href='/static/Raleway.css'),



    # header div
    html.Div([
        html.Div([
            html.Div([
                html.Div(["Related Articles"], id="header"),
                html.Div([dcc.Link('選手データを追加する', href='/add_logs_to_models', id='header-right')],
                         style={'cursor': 'pointer', 'float': 'right', 'margin-right': '7%'}),
                html.Div([dcc.Link('TOP', href='/', id='header-right')],
                         style={'cursor': 'pointer', 'float': 'right'})
            ]),
        ],id="header-bk", style={'font-family': 'Montserrat', 'width': '100%'}),
    ],id="header-fixed"),

    # title
    html.Div([
        html.H1(['TRAINING OPT'], id='title_h')
    ], style={'width': '100%', 'text-align':'center'})
])

# define footer conponents (reusable)
footer_components = html.Div([
    # footer div
    html.Div([
        html.Div([
            html.Div([html.A('©️Sasaki Kensuke ', href='https://qiita.com/sasaki_K_sasaki/items/6eb67a218c06dd56778e')], id="footer")
        ],id="footer-bk")
    ],id="footer-fixed")
])


# define toppage layout ------------------------

page_1_layout = html.Div([

    title_components,

    # dropdown div
    html.Div([

        # define dropdown input
        html.Div([
            dcc.Dropdown(
                placeholder='please select article title ...',
                id='dropdown-input',
                options=[{'label': i, 'value': j} for i,j in zip(processing.body_data.title.unique(),
                                                                 processing.body_data.article_num.unique())]
            )
        ], style={'margin-bottom': '3%',
                  'width': '90%',
                  'font-size': '12px',
                  'font-style': 'Noto Sans JP',
                  'position': 'auto', 'margin': 'auto'}),

        # define the way of recommendation
        html.Div([
            dcc.RadioItems(
            # dcc.Checklist(
                options=[{'label': 'Nginx log', 'value': 'way_log'},
                         {'label': 'Contents', 'value': 'way_contents'},
                         {'label': 'Titles', 'value': 'way_titles'}],
                id='radio-input',
                className='state',
                labelClassName='state',
                value='way_log',
                labelStyle={'display': 'inline-block',
                            'margin': '3% 6%',
                            'color': '#373939',
                            'font-size': '24px',
                            'font-style': 'bold',
                            'font-family' : 'Montserrat'})
        ], className='pretty', style={'position': 'auto', 'margin': 'auto', 'text-align': 'center'}),


        # define table app_layout
        html.Div([
            dt.DataTable(
                rows=[{}], # initialise the rows
                header_row_height="50px",
                enable_drag_and_drop=False,
                # min_width="100%",
                row_selectable=False,
                filterable=False,
                sortable=True,
                # selected_row_indices=[],
                id='datatable'
            )], style={'width': '90%', 'position': 'auto', 'margin': 'auto', 'max-width':'1100px'}
        ),

        footer_components

    ],
    style={'width': '100%', 'position': 'auto', 'margin': 'auto'}),
],
id='wrapper',
style={'position': 'relative', 'width': '100%', 'font-family': 'Noto Sans JP'})

# Update tables in a callback
@app.callback(Output('datatable', 'rows'),
              [Input('dropdown-input', 'value'),
               Input('radio-input', 'value')])
def update_datatable(user_selection, radio_value):
    """
    For user selections, return the relevant table
    """
    if radio_value=="way_log":
        top_df_use = processing.log_data
    elif radio_value=="way_contents":
        top_df_use = processing.body_data
    else:
        top_df_use = processing.title_data

    returned_df = processing.show_selected_table(df=top_df_use,
                                                 df_link=processing.link_data,
                                                 df_rellink=processing.rellink_data,
                                                 input_value=user_selection,
                                                 input_rvalue=radio_value)
    return returned_df



# define page2 layout ------------------------

input_style = { 'border':'0',
                'padding':'10px',
                'font-size':'1em',
                'font-family':'Arial, sans-serif',
                'color':'#aaa',
                'border':'solid 1px #ccc',
                'margin':'0 0 20px',
                'width':'100%',
                '-webkit-border-radius': '3px',
                '-moz-border-radius': '3px',
                'border-radius': '3px' }

page_2_layout = html.Div([

    title_components,

    html.Div([
        html.Div([
                html.H2("新規記事タイトルを入力してください.."),
                dcc.Input(id='input-box',
                          type='url',
                          placeholder='please write Article title ...',
                          style=input_style),
                html.H2("新規記事本文を入力してください.."),
                dcc.Textarea(
                    id='input-contents',
                    placeholder='please write Article contents ...',
                    style=input_style
                )
                  ],
                 style={'width': '100%'}),
        html.Button('Submit', id='button', className='square_btn', style={'margin-bottom': '3%'}),
        html.Div(id='output-container-button',
                 children='Enter a value and press submit')
    ], style={'width': '100%', 'color': '#373939', 'font-style': 'Noto Sans JP' }),

    footer_components

],id='wrapper',
style={'position': 'relative', 'width': '100%', 'font-family': 'Noto Sans JP'})


def lower_text(text):
    return text.lower()

def extractKeyword(text):
    # normalize text
    text = neologdn.normalize(lower_text(text))
    # define tagger
    tagger = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    node = tagger.parseToNode(text)#textがu''形式⇒『.encode()』が必要
    keywords = []
    while node:
        if node.feature.split(",")[0] == "名詞" or node.feature.split(",")[0] == "動詞":
            keywords.append(node.surface)
        node = node.next
    return keywords

@app.callback(Output('output-container-button', 'children'),
              [Input('button', 'n_clicks')],
              [State('input-box', 'value')])
def update_output(n_clicks, value):
    keywords = extractKeyword(value)
    res = []
    for w in keywords:
        res.append(w)
    return 'RESULT : "{}" CLICKED {} times'.format(
        res,
        n_clicks
    )


# define page3 layout -------------------------------------------------------------------------------


page_3_layout = html.Div([

    title_components,

    html.Div([
        html.Div([
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=False)
        ])
    ], style={'width': '100%','position': 'auto', 'margin': 'auto'}),

    html.Div(dt.DataTable(rows=[{}], id='table')),


    footer_components

],id='wrapper',
style={'position': 'relative', 'width': '100%', 'font-family': 'Montserrat'})


# file upload function
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv( io.StringIO(decoded.decode('utf-8')) )
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))

    except Exception as e:
        print(e)
        return None

    return df




# callback table creation
@app.callback(Output('table', 'rows'),
              [Input('upload-data', 'contents'),
               Input('upload-data', 'filename')])
def update_output(contents, filename):
    if contents is not None:
        # このparse_contentsで今はcsvを読み込んでdfに代入する仕様になってて、
        # このparse_contentsの他に新しく関数を定義して、jsonを読み込んで記事×記事データを返してくれるようにしてくれると良いです！！
        df = parse_contents(contents, filename)
        if df is not None:
            return df.to_dict('records')
        else:
            return [{}]
    else:
        return [{}]



# end of page3 layout -------------------------------------------------------------------------------


# define whole layout ------------------------

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'}),
    html.Div(id='page-content')
])


# --------------------------- app_table return logic ---------------------------


# Update the index
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return page_1_layout
    elif pathname == '/add_articles_to_models':
        return page_2_layout
    elif pathname == '/add_logs_to_models':
        return page_3_layout
    # You could also return a 404 "URL not found" page here


# --------------------------- add stylesheet ---------------------------

@app.server.route('/static/<path:path>')
def static_file(path):
    static_folder = os.path.join(os.getcwd(), 'static')
    return send_from_directory(static_folder, path)



if __name__ == '__main__':
    app.run_server(debug=True, port=5000, host='0.0.0.0')
