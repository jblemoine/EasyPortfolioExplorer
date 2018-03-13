import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

from .dropdown import MultiEasyDropdown


class EasyLayout(MultiEasyDropdown):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_resources()
        self.add_skeleton()

    def add_skeleton(self):
        self.app.layout = html.Div([
            dcc.Location(id='url', refresh=False),  # not rendered

            # this is a bug correction, more info see: https://community.plot.ly/t/display-tables-in-dash/4707/39
            html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'}),  # not rendered

            html.Div([
                html.H1('Easy Portfolio Explorer', className='text-center')],
                className='page-header'),

            html.Div(
                html.Div(self.dropdowns(className='col-xs-4 col-xs-offset-0.5'), className='row'),
                id='dropdown-cont'),

            html.Div(
                self._main_graph(),
                className='row',
            ),

            html.Div(
                self._slider(),
                className='row'
            ),
            html.Div(
                self._links(className='btn-primary btn-lg'),
                className='row',
                id='tabs'
            ),
            html.Div(
                id='tab-output'
            ),
            html.Footer(
                id='footer',
                className='footer'
            )

        ], className='container-fluid')

    @staticmethod
    def _main_graph():

        return[
            dcc.Graph(
                id='main-graph',
                animate=True
            )
        ]

    def _slider(self):

        return [
            html.Div([

                dcc.RangeSlider(
                    min=0,
                    max=len(self.date_range) - 1,
                    step=None,
                    marks={index: date.strftime("%d-%m-%Y") for index, date in enumerate(self.date_range)},
                    value=[0, len(self.date_range) - 1],
                    id='RangeSlider')
                ],
                className='col-xs-10 col-xs-offset-1 custom_margin')
        ]

    @staticmethod
    def _links(className):

        buttons = [
            dcc.Link('Portfolio record', href="/portfolio_record", className=className),
            dcc.Link('Past performance', href="/past_performance", className=className),
            dcc.Link('Latest transactions', href="/latest_transactions", className=className),
            dcc.Link('Risk Analysis', href="/risk_analysis", className=className),
            dcc.Link('User comments', href="/user_comments", className=className)
        ]

        return [html.Div(button, className='col-xs-2 button') for button in buttons]

