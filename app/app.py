import os
import io
import sys
import dash
import plotly
import sqlite3
import dash_auth_edit as dash_auth
import loremipsum
import numpy as np
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output, State

from flask_caching import Cache
from flask import send_from_directory
from loremipsum import get_sentences



# --------------------------- preprocessing ---------------------------

# user database
conn_user = sqlite3.connect("data/user_db.db")
df_user_table = pd.read_sql("select * from user_table", conn_user)


# --------------------------- define app ---------------------------

# Keep this out of source code repository - save in a file or a database
VALID_USERNAME_PASSWORD_PAIRS = [
    [name, passward] for name,passward in  zip(df_user_table.Name, df_user_table.Passward)
]
app = dash.Dash('auth')
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)
app.title = 'Query Share'
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
app.config.suppress_callback_exceptions = True

CACHE_CONFIG = {
    # try 'filesystem' if you don't want to setup redis
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'localhost:6379')
}
cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)


# current _username
c_username = auth._username_password_list[0][0]
# c_username = auth.get_username()_


# sql database
conn_sqldb = sqlite3.connect("data/sql_db.db")
df_sql_table = pd.read_sql("select * from sql_table", conn_sqldb)
sql_table_current = df_sql_table.query('ID in "' + c_username + '"')



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
                html.Div(["Query Share"], id="header"),
                html.Div([dcc.Link(c_username, href='/profile', id='header-right')],
                         style={'cursor': 'pointer', 'float': 'right', 'margin-right': '7%'}),
                html.Div([dcc.Link("New query", href='/add_file', id='header-right')],
                         style={'cursor': 'pointer', 'float': 'right'}),
                html.Div([dcc.Link('TOP', href='/', id='header-right')],
                         style={'cursor': 'pointer', 'float': 'right'})
            ]),
        ],id="header-bk", style={'font-family': 'Montserrat', 'width': '100%'}),
    ],id="header-fixed"),

    # title
    html.Div([
        # html.H1(['Query Share'], id='title_h')
        html.H1([''], id='title_h')
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

    html.Div([

        html.Div([
            dcc.Tabs(
                tabs=[{'label': i, 'value': j} for i,j in zip(sql_table_current.Name,
                                                              sql_table_current.index.tolist())
                ],
                value=1,
                id='tabs',
                # vertical=False,
                style={
                    'font-family': 'Montserrat'
                    }
            ),
            html.Div(id='tab-output')
        ], style={
            'width': '100%',
            'margin-left': 'auto',
            'margin-right': 'auto',
            'margin-bottom': '5%'
        }),



        footer_components

    ],
    style={'width': '100%', 'position': 'auto', 'margin': 'auto'}),

],
id='wrapper',
style={'position': 'relative', 'width': '100%', 'font-family': 'Noto Sans JP'})



@app.callback(Output('tab-output', 'children'),
              [Input('tabs', 'value')])
def display_content(value):
    test_query=[statement for statement in sql_table_current.Statement],

    return html.Div([
        html.Br(),
        html.Div([
        dcc.Textarea(
            id="input_query",
            placeholder='Please write query',
            value=test_query[0][value-1],
            style={'width': '99%',
                   'display': 'table',
                   'position': 'auto',
                   'margin': 'auto',
                   'margin-left':'2px',
                   'height': "200px",
                   'font-family':'Monaco',
                   'font-size': "18px",
                   'border': 'solid 2px #2bb6c1',
                   'border-radius': '4px'
                   }

        )],style={'width' : '100%'}
        ),
        html.Div([
        html.Div([
            html.Ul([
                html.Li(html.Button('RUN',
                                     id='button-run',
                                     className='button-bop')),
                html.Li(html.Button('SAVE',
                                     id='button-save',
                                     className='button-bop')),
            ], style={'list-style':'none',
                      'border': 'none',
                      'display': 'flex',
                      'justify-content': 'flex-end'})
        ], id="holder")], className="container-wrap"),
    # define table app_layout
    html.Div([
        dt.DataTable(
            rows=[{}], # initialise the rows
            # header_row_height="50px",
            enable_drag_and_drop=False,
            # min_width="100%",
            row_selectable=False,
            filterable=False,
            sortable=True,
            id='datatable'
        )], style={'width': '90%',
                   'height': '90%',
                   'position': 'auto',
                   'margin': 'auto',
                   'max-width':'1100px',
                   'margin-top': '24px',
                   'margin-bottom':'24px'}
    )
    ], style={
        'background-color': "white"
    })
@app.callback(Output('datatable', 'rows'),
              [Input('button-run', 'n_clicks'),
               Input('tabs', 'value')],
              [State('input_query', 'value')])
def execte_query(n_clicks, tab_value, value):
    # dbに対してTextareaのvalueを実行
    conn = sqlite3.connect("data/sql_db.db")
    # define statement
    statement = value
    df_fromdb = pd.read_sql(statement, conn)

    # RUNのstatementに変更
    c = conn_sqldb.cursor()
    change_commit_sql = "UPDATE sql_table SET Statement = {} WHERE Index = {}".format(value, tab_value-1)
    c.execute(change_commit_sql)
    conn_sql.commit()
    # UPDATE テーブル名 SET カラム名 = 更新後の値 where name = 更新前の値;

    return df_fromdb.to_dict('records')

# @app.callback([Input('button-save', 'n_clicks')],
#               [State('input_query', 'value')])
# def execte_query(n_clicks, value):
#     c = conn_sqldb.cursor()
#     # データ追加(レコード登録)
#     sql = 'insert into sql_table (ID, Name, Statement) values (?,?,?)'
#     data = ('qs_user1', "add_sample.sql", "SELECT * FROM TEST")
#     c.execute(sql, data)
#     # コミット
#     conn_sql.commit()




















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
                html.H2("New file name."),
                dcc.Input(id='input-box',
                          type='url',
                          placeholder='please write filename',
                          style=input_style)
                  ],
                 style={'width': '100%'}),
        html.Button('Create', id='button', className='button-bop', style={'margin-bottom': '3%'}),
        html.Div(id='output-container-button',
                 children='Enter a value and press submit'),
        html.Div(id="save-output")
    ], style={'width': '100%', 'color': '#373939', 'font-style': 'Noto Sans JP' }),

    footer_components

],id='wrapper',
style={'position': 'relative', 'width': '100%', 'font-family': 'Noto Sans JP'})

@app.callback(Output('save-output', 'children'),
              [Input('button-save', 'n_clicks')],
              [State('input_name', 'value')])
def execte_query(value):
    c = conn_sqldb.cursor()
    # データ追加(レコード登録)
    sql = 'insert into sql_table (ID, Name, Statement) values (?,?,?)'
    data = (c_username, value, "")
    c.execute(sql, data)
    # コミット
    conn_sql.commit()
    return html.Div("New file has created.")


page_3_layout = html.Div([

    title_components,

    html.Div([
        html.Div([
                html.H3("User Name is {}".format(c_username)),
                html.Br(),
                html.H3("Recent work is {}".format(max(df_user_table.Date))),
                html.Br(),
                html.Div([sql for sql in sql_table_current.Name])
                  ],
                 style={'width': '100%'})
    ], style={'width': '100%', 'color': '#373939' }),

    footer_components

],id='wrapper',
style={'position': 'relative', 'width': '100%', 'font-family': 'Noto Sans JP'})















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
    elif pathname == '/add_file':
        return page_2_layout
    elif pathname == '/profile':
        return page_3_layout
    else:
        return html.Div("404 Not Found.")
    # You could also return a 404 "URL not found" page here


# --------------------------- add stylesheet ---------------------------

@app.server.route('/static/<path:path>')
def static_file(path):
    static_folder = os.path.join(os.getcwd(), 'static')
    return send_from_directory(static_folder, path)



if __name__ == '__main__':
    app.run_server(debug=True, port=5000, host='0.0.0.0')
