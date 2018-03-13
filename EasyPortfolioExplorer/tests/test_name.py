from EasyPortfolioExplorer import names


def test_get_full_name():

    for _ in range(1000):
        assert names.get_full_name() is not None
