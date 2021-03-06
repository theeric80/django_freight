from django.core.management.base import BaseCommand, CommandError

from prettytable import PrettyTable

from apps.commodities.models import Inventory


class Command(BaseCommand):
    help = 'run "manage.py list_all_glutted_commodity --quantity=100" will show all commodities whose quantity >= 100'

    def add_arguments(self, parser):
        # Positional arguments

        # Named (optional) arguments
        parser.add_argument('--quantity', type=int, default=100)

    def handle(self, *args, **options):
        quantity = options['quantity']
        if quantity < 0:
            raise CommandError('Negavite quantity Value')

        glutted_commodities = Inventory.objects.list_glutted_commodities(quantity) \
            .values_list('commodity__id', 'commodity__name', 'total_quantity')


        table = PrettyTable()
        table.field_names = ['id', 'Name', 'Quantity']
        for commodity in glutted_commodities:
            table.add_row(commodity)

        self.stdout.write(str(table))
