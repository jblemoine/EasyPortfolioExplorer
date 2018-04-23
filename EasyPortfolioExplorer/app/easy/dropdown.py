import dash_core_components as dcc
from pandas import DataFrame

from .storage import Storage


class EasyDropdown(dcc.Dropdown):
    """
    A custom dropdown element. All instances will communicate between each other and update their content automatically.

    """
    _instances = []

    def __init__(self, data: DataFrame, label: str, id=None, **kwargs):
        super().__init__(**kwargs)
        self.id = id if id else label
        self.label = label
        self.data = data
        self.options = [{'label': value,
                         'value': value} for value in self.data[self.label].unique()]
        self._position = len(EasyDropdown._instances)

        if self._position > 0:
            self.previous_drpdwn = self.get_instances()[-1]
        EasyDropdown._instances.append(self)

    def get_available_data(self, filtered_values):
        temp_df = self.previous_drpdwn.data

        if filtered_values:
            self.data = temp_df[temp_df[self.previous_drpdwn.id].isin(filtered_values)]

        else:
            self.data = temp_df
        return self.data

    @classmethod
    def get_instances(cls):
        return cls._instances

    def _update_options(self, values, options):
        available_data = self.get_available_data(values)

        return [{'label': value, 'value': value} for value in available_data[self.label].unique()]


class MultiEasyDropdown(Storage):
    """
    This class create the dropdown present in the app.

    """

    def __init__(self, labels: list, **kwargs):

        super().__init__(**kwargs)
        self._dropdowns = None

        for label in labels:
            if label not in self.df.columns:
                raise (ValueError, "{} is a wrong label, can be either: {}".format(label, list(self.df.columns)))

        self.labels = labels

    def dropdowns(self, className=None, multi=True):
        """
        Create list of custom dropdowns.

        :param className: Sets the class name of the element (the value of an element's html class attribute).
        :param multi: If True, the user can select multiple values.
        :return: list of dropdowns. The last element is hidden.
        """
        if not self._dropdowns:
            self._dropdowns = [EasyDropdown(label=label, data=self.df, id=label, className=className, multi=multi)
                              for label in self.labels] + [EasyDropdown(label=self.labels[-1],
                                                                        data=self.df,
                                                                        id='hidden-dropdown',
                                                                        multi=multi,
                                                                        className='hidden'
                                                                        )]
        return self._dropdowns




