from setuptools import setup

setup(
    name='easy_portfolio_explorer',
    version='0.1',
    author='Jean-Baptiste Lemoine',
    author_email='j.lemoine@tbs-education.org',
    packages=['easy_portfolio_explore'],
    include_package_data=True,
    description='Portfolio Explorer based on Dash.',
    install_requires=['pandas',
                      'numpy',
                      'dash',
                      'dash-core-components',
                      'dash-html-components',
                      'names',
                      'dash-table-experiments']
)