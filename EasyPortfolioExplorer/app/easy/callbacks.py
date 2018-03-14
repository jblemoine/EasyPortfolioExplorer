import dash_html_components as html
import numpy as np
import plotly.graph_objs as go
from dash.dependencies import Output, Input, State

from .layout import EasyLayout
from EasyPortfolioExplorer.app.utils.tab import portfolio_record, past_perf, user_coments, export_comment, risk_analysis


class EasyCallbacks(EasyLayout):

    def __init__(self, **kwargs):

        super(EasyCallbacks, self).__init__(**kwargs)

        for dropdown in self.dropdowns()[1:]:
            self.app.callback(Output(dropdown.id, 'options'),
                              [Input(dropdown.previous_drpdwn.id, 'value'),
                               Input(dropdown.previous_drpdwn.id, 'options')]
                              )(dropdown._update_options)

        self.app.callback(
            Output('main-graph', 'figure'),
            [Input(self.dropdowns()[-1].id, 'value'),
             Input(self.dropdowns()[-1].id, 'options'),
             Input('RangeSlider', 'value'),
             Input('RangeSlider', 'marks')]

        )(self._update_graph)

        self.app.callback(
            Output('tab-output', 'children'),
            [Input('url', 'pathname'),
             Input('main-graph', 'clickData'),
             Input('RangeSlider', 'value'),
             Input('RangeSlider', 'marks')
             ]
        )(self._update_tab_output)

        self.app.callback(
            Output('comment-output', 'children'),
            [Input('comment-button', 'n_clicks'),
             Input('tab-output', 'children'),
             Input('main-graph', 'clickData')],
            [State('comment-input', 'value')]
        )(self._export_comment)

    def _update_graph(self, value, options, slider_value, slider_marks):

        last_dropdwn = self.dropdowns()[-1]
        start = slider_marks[str(slider_value[0])]
        end = slider_marks[str(slider_value[1])]

        if value:
            last_dropdwn.data = last_dropdwn.data[last_dropdwn.data[last_dropdwn.id].isin(value)]

        self._compute_returns(start=start, end=end)
        self._compute_variance(start=start, end=end)

        returns = last_dropdwn.data["Return_from_{0}_to_{1}".format(start, end)]
        std = np.sqrt(last_dropdwn.data["Variance_from_{0}_to_{1}".format(start, end)])
        sharpe = returns/std

        figure = go.Figure(
            data=[
                go.Scatter(
                    y=returns,
                    x=std,
                    mode='markers',
                    hoverinfo="text",
                    #name=str(profile),
                    marker=go.Marker(
                        size=8,
                        color=sharpe,
                        colorscale='Jet',
                        opacity=0.8,
                        line=go.Line(width=0.5)

                    ),
                    text="Fund number: " + last_dropdwn.data['id'].astype(str) + "<br>"
                    + "Fund Manager: " + last_dropdwn.data['Fund_manager'] + "<br>"
                    + "Return over the period: " + (last_dropdwn.data["Return_from_{0}_to_{1}".format(start, end)]*100).map(lambda x: "{0:.2f}%".format(x)) + "<br>"
                    + "Annualised Standard Deviation: " + (np.sqrt(last_dropdwn.data["Variance_from_{0}_to_{1}".format(start, end)])*100).map(lambda x: "{0:.2f}%".format(x)) + "<br>"
                    + "Creation date: " + last_dropdwn.data['Creation_date'].dt.strftime('%Y-%m-%d')
                )], #for profile, data in grouped],

            layout=go.Layout(
                hovermode='closest',
                title='Perf vs VaR',
                xaxis=go.XAxis(
                    title='Adjusted Volatility'
                ),
                yaxis=go.YAxis(
                    title='Return over the period'
                )
            )
        )
        return figure

    def _update_tab_output(self, pathname, clickData, slider_value, slider_marks):
        start = slider_marks[str(slider_value[0])]
        end = slider_marks[str(slider_value[1])]

        if clickData is None:
            return html.Div(style={'display': 'none'})

        else:
            id = clickData['points'][0]['text'][13:25]
            portfolio = self.df.loc[self.df['id'] == id, 'Portfolio'].iloc[0]

        if pathname == '/portfolio_record':
            return portfolio_record(portfolio)

        elif pathname == '/past_performance':
            return past_perf(portfolio)

        elif pathname == '/latest_transactions':
            pass

        elif pathname == '/risk_analysis':
            return risk_analysis(portfolio, start, end)

        elif pathname == '/user_comments':
            return user_coments(portfolio)

    def _export_comment(self, n_click, children, clickData, value):

        id = clickData['points'][0]['text'][13:25]
        portfolio = self.df.loc[self.df['id'] == id, 'Portfolio'].iloc[0]

        if n_click:
            export_comment(value, portfolio)
            return "Comment exported with success."

#











