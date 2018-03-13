import sqlite3
from datetime import date

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dtex
import pandas as pd
import plotly.graph_objs as go

from easy.portfolio import RandomPortfolio


def portfolio_record(portfolio: RandomPortfolio):
    frame = pd.DataFrame([portfolio.tickers, portfolio.weights]).T
    frame.columns = ['Ticker', "Weight"]
    frame['Weight'] = (frame['Weight']*100).map(lambda x: "{0:.2f}%".format(x))

    return html.Div([
        html.H1("Account n° {} - Portfolio records".format(portfolio.id), className='panel-heading'),
        dtex.DataTable(
            rows=frame.to_dict('records'),
            filterable=True,
            sortable=True,
            id='records_table'
        )
    ], className='panel panel-default')


def past_perf(portfolio: RandomPortfolio):
    ptf_histo_value = portfolio.ptf_histo_value(start='20070101', end=date.today().strftime("%Y%m%d"))

    return html.Div([
        html.H2('Account n° {} - Historical return'.format(portfolio.id), className='panel-heading'),
        html.Div([

            dcc.Graph(figure=go.Figure(
                data=[go.Scatter(
                    y=ptf_histo_value,
                    x=ptf_histo_value.index,
                    hoverinfo="text",
                    text="Value: " + ptf_histo_value.round(2).astype(str) + "<br>" + ptf_histo_value.index.strftime("%Y-%m-%d")
                )],
                layout=go.Layout(
                    title='Historical performance',
                    hovermode='closest')
                ),

                animate=False,
                id='past-perf'
            )],
            className='panel-body')

    ], className='panel panel-default')


def user_coments(portfolio: RandomPortfolio):

    with sqlite3.connect('data/comments.db') as conn:
        c = conn.cursor()

        c.execute("""
                CREATE TABLE IF NOT EXISTS comment_table(
                  id varchar(12),
                  user TEXT,
                  date DATE,
                  text TEXT,
                  tag TEXT)
                  """)

        existing_comments = pd.read_sql("""
            SELECT * FROM comment_table 
            WHERE id = {};""".format(portfolio.id), con=conn)

        if existing_comments.empty:
            comments_table = html.P("No existing comments for this portfolio.")
        else:
            comments_table = dtex.DataTable(
                rows=existing_comments.to_dict('records'),
                filterable=True,
                sortable=True,
                id='existing-comments')

    return html.Form(

        html.Div([

            html.H2('Account n° {} - Comments'.format(portfolio.id), className='panel-heading'),

            html.Div([
                html.Div([

                    comments_table,
                    html.Label('Comments', htmlFor='comment-input'),
                    dcc.Textarea(
                        id='comment-input',
                        value='',
                        placeholder='Enter a comments...',
                        rows=4,
                        className='form-control'),
                        ],
                    className='form-group'),

                html.Div([
                    html.Button('Submit', id='comment-button', n_clicks=None, className='btn btn-default'),
                    html.Div(id='comment-output')],

                    className='form-group')

                ],
                className='panel-body')

        ], className='panel panel-default'),
    )


def risk_analysis(portfolio: RandomPortfolio, start, end):

    betas = portfolio.indices_beta(start=start, end=end)

    return html.Div([
        html.H2('Account n° {} - Risk Analysis'.format(portfolio.id), className='panel-heading'),
        html.Div([

            dcc.Graph(figure=go.Figure(
                data=[go.Bar(
                    y=betas.values,
                    x=betas.index,
                    hoverinfo="text",
                    text="Index: " + betas.index + "<br>" + "Beta: " + betas.values.round(2).astype(str)
                )],
                layout=go.Layout(
                    title='Portfolio Beta to major indices.',
                    hovermode='closest')
                ),

                animate=False,
                id='indices-beta'
            )],
            className='panel-body')

    ], className='panel panel-default')


def export_comment(value, portfolio: RandomPortfolio):
    with sqlite3.connect('data/comments.db') as conn:

        c = conn.cursor()
        c.execute("""
        INSERT INTO comment_table(date, text, id)
          VALUES(?,?,?);""", (date.today(), str(value), portfolio.id))
        # pop up: Are you sure you want to commit ?

        conn.commit()











