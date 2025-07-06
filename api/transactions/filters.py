from dj_rql.filter_cls import AutoRQLFilterClass
from transactions.models import Category, Description, Transaction


class CategoryFilterClass(AutoRQLFilterClass):
    MODEL = Category


class DescriptionFilterClass(AutoRQLFilterClass):
    MODEL = Description
    FILTERS = [
        {
            'filter': 'category',
            'source': 'category__name'
        }
    ]


class TransactionFilterClass(AutoRQLFilterClass):
    MODEL = Transaction
    FILTERS = [
        {
            'filter': 'category',
            'source': 'category__name'
        },
        {
            'filter': 'description',
            'source': 'description__name'
        },
        {
            'filter': 'user',
            'source': 'user__username'
        },
    ]
