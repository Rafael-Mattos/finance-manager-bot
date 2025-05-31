from dj_rql.filter_cls import AutoRQLFilterClass, FilterLookups
from transactions.models import Group, Description, Transaction, Recurring


class GroupFilterClass(AutoRQLFilterClass):
    MODEL = Group

    
class DescriptionFilterClass(AutoRQLFilterClass):
    MODEL = Description
    FILTERS = [
        {
            'filter':  'group',
            'source': 'group__name'
        }
    ]

class TransactionFilterClass(AutoRQLFilterClass):
    MODEL = Transaction
    FILTERS = [
        {
            'filter':  'group',
            'source': 'group__name'
        },
        {
            'filter':  'description',
            'source': 'description__name'
        },
        {
            'filter':  'user',
            'source': 'user__username'
        },
    ]


class RecurringFilterClass(AutoRQLFilterClass):
    MODEL = Recurring
    FILTERS = [
        {
            'filter':  'group',
            'source': 'group__name'
        },
        {
            'filter':  'description',
            'source': 'description__name'
        },
        {
            'filter':  'user',
            'source': 'user__username'
        },
    ]

