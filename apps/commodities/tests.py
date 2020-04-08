from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User
from apps.commodities.models import Commodity, Inventory, InventoryHistory

# Create your tests here.
class InventoryViewSetTestCase(APITestCase):
    username = 'lauren'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ...

    @classmethod
    def tearDownClass(cls):
        # ...
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = User.objects.create(username=cls.username)

        c1 = Commodity.objects.create(name='test_commodity_1')
        c2 = Commodity.objects.create(name='test_commodity_2')
        cls.commodity = c1

        shipping = Inventory.Type.SHIPPING
        receiving = Inventory.Type.RECEIVING
        cls.inventories = [
            Inventory.objects.create(type=shipping,  quantity=1, commodity=c1),
            Inventory.objects.create(type=receiving, quantity=2, commodity=c1),
            Inventory.objects.create(type=shipping,  quantity=3, commodity=c2),
            Inventory.objects.create(type=receiving, quantity=4, commodity=c2),
        ]

    def setUp(self):
        super().setUp()

        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        super().tearDown()

    def test_list_view(self):
        #When
        url = reverse('inventory-list')
        response = self.client.get(url)

        # Then
        expected_fields = ['id', 'type', 'quantity', 'commodity_name']
        expected_count = len(self.inventories)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], expected_count)

        for i, data in enumerate(response.data['results']):
            expected = self.inventories[i]

            self.assertCountEqual(data.keys(), expected_fields)

            self.assertEqual(data['id'], expected.pk)
            self.assertEqual(data['type'], expected.type)
            self.assertEqual(data['quantity'], expected.quantity)
            self.assertEqual(data['commodity_name'], expected.commodity.name)

    def test_create_view(self):
        # Given
        expected = {
            'type': Inventory.Type.SHIPPING,
            'quantity': 1,
            'commodity': self.commodity.pk,
        }

        # When
        url = reverse('inventory-list')
        response = self.client.post(url, data=expected)
        data = response.data

        # Then
        expected_fields = ['id', 'type', 'quantity', 'commodity', 'trade_partner']

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertCountEqual(data.keys(), expected_fields)

        self.assertEqual(data['type'], expected['type'])
        self.assertEqual(data['quantity'], expected['quantity'])
        self.assertEqual(data['commodity'], expected['commodity'])

        history = InventoryHistory.objects.last()
        self.assert_inventory_history_match(
            history, InventoryHistory.Action.ADD, self.user)

    def test_retrieve_view(self):
        # Given
        expected = self.inventories[0]

        # When
        url = reverse('inventory-detail', args=[expected.pk])
        response = self.client.get(url)
        data = response.data

        # Then
        expected_fields = ['id', 'type', 'quantity', 'commodity', 'trade_partner']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(data.keys(), expected_fields)

    def test_update_view(self):
        # Given
        fields = {
            'type': Inventory.Type.SHIPPING,
            'quantity': 1,
            'commodity': self.commodity,
        }
        inventory = Inventory.objects.create(**fields)

        expected = {
            'type': Inventory.Type.RECEIVING,
            'quantity': 2
        }

        # When
        url = reverse('inventory-detail', args=[inventory.pk])
        response = self.client.put(url, data=expected)
        data = response.data

        # Then
        expected_fields = ['id', 'type', 'quantity', 'commodity', 'trade_partner']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(data.keys(), expected_fields)

        self.assertEqual(data['id'], inventory.pk)
        self.assertEqual(data['type'], expected['type'])
        self.assertEqual(data['quantity'], expected['quantity'])

        history = InventoryHistory.objects.last()
        self.assert_inventory_history_match(
            history, InventoryHistory.Action.MODIFY, self.user)

    def test_destroy_view(self):
        # Given
        fields = {
            'type': Inventory.Type.SHIPPING,
            'quantity': 1,
            'commodity': self.commodity,
        }
        inventory = Inventory.objects.create(**fields)

        # When
        url = reverse('inventory-detail', args=[inventory.pk])
        response = self.client.delete(url)

        # Then
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertRaises(Inventory.DoesNotExist, Inventory.objects.get, pk=inventory.pk)

        history = InventoryHistory.objects.last()
        self.assert_inventory_history_match(
            history, InventoryHistory.Action.DELETE, self.user)

    def test_summary_view(self):
        # When
        url = reverse('inventory-summary')
        response = self.client.get(url)

        # Then
        expected_fields = [
            'commodity_id',
            'commodity_name',
            'total_quantity',
            'shipping_quantity',
            'receiving_quantity',
        ]
        expected_count = 2
        expected = [
            {
                'commodity_id': 1,
                'total_quantity': 3,
                'shipping_quantity': 1,
                'receiving_quantity': 2,
            },
            {
                'commodity_id': 2,
                'total_quantity': 7,
                'shipping_quantity': 3,
                'receiving_quantity': 4,
            },
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], expected_count)

        for i, data in enumerate(response.data['results']):
            self.assertCountEqual(data.keys(), expected_fields)

            self.assertEqual(data['total_quantity'], expected[i]['total_quantity'])
            self.assertEqual(data['shipping_quantity'], expected[i]['shipping_quantity'])
            self.assertEqual(data['receiving_quantity'], expected[i]['receiving_quantity'])

    def assert_inventory_history_match(self, history, action, user):
        self.assertEqual(history.action, action)
        self.assertEqual(history.user, user)
