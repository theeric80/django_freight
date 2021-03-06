from django.test import TestCase
from django.urls import reverse
from django.http import Http404

from model_bakery import baker

from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.test import APIRequestFactory, APISimpleTestCase, APITestCase

from apps.commodities.views import LinkHeaderPagination
from apps.commodities.models import Inventory, InventoryHistory

# Create your tests here.
class InventoryViewSetTestCase(APITestCase):

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

        cls.user = baker.make_recipe('apps.users.user')

    def setUp(self):
        super().setUp()

        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        super().tearDown()

    def test_list_view(self):
        # Given
        expected_count = 3
        inventories = baker.make_recipe('apps.commodities.inventory', _quantity = expected_count)

        # When
        url = reverse('inventory-list')
        response = self.client.get(url)

        # Then
        expected_fields = ['id', 'type', 'quantity', 'commodity_name']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], expected_count)

        for i, data in enumerate(response.data['results']):
            expected = inventories[i]

            self.assertCountEqual(data.keys(), expected_fields)

            self.assertEqual(data['id'], expected.pk)
            self.assertEqual(data['commodity_name'], expected.commodity.name)

    def test_create_view(self):
        # Given
        expected = {
            'type': Inventory.Type.SHIPPING,
            'quantity': 1,
            'commodity': baker.make_recipe('apps.commodities.commodity').pk,
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
        expected = baker.make_recipe('apps.commodities.inventory')

        # When
        url = reverse('inventory-detail', args=[expected.pk])
        response = self.client.get(url)
        data = response.data

        # Then
        expected_fields = ['id', 'type', 'quantity', 'commodity', 'trade_partner']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(data.keys(), expected_fields)
        self.assertEqual(data['id'], expected.pk)

    def test_update_view(self):
        # Given
        inventory = baker.make_recipe('apps.commodities.inventory')
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
        inventory = baker.make_recipe('apps.commodities.inventory')

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
        # Given
        shipping = Inventory.Type.SHIPPING
        receiving = Inventory.Type.RECEIVING

        c1 = baker.make_recipe('apps.commodities.commodity')
        c2 = baker.make_recipe('apps.commodities.commodity')

        baker.make_recipe('apps.commodities.inventory', type=shipping,  quantity=1, commodity=c1)
        baker.make_recipe('apps.commodities.inventory', type=receiving, quantity=2, commodity=c1)
        baker.make_recipe('apps.commodities.inventory', type=shipping,  quantity=3, commodity=c2)
        baker.make_recipe('apps.commodities.inventory', type=receiving, quantity=4, commodity=c2)

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

class LinkHeaderPaginationTestCase(APISimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.factory = APIRequestFactory()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_link(self):
        # Given
        url, page, size, rel = '/api/pages/', 0, 30, 'next'
        request = self.factory.get(url)
        queryset = [1]
        expected = '<http://testserver{}?page={}&page_size={}>; rel="{}"'.format(
            url, page, size, rel)

        # When
        paginator = LinkHeaderPagination()
        paginator.paginate_queryset(queryset, request)
        link = paginator.get_link(page, size, rel)

        # Then
        self.assertEqual(link, expected)

    def test_paginate_queryset_empty_page(self):
        # Given
        page, page_size, url = 2, api_settings.PAGE_SIZE, '/api/pages/'
        request = self.factory.get(url, {'page': page})
        queryset = [1]

        # When
        with self.assertRaises(Http404):
            paginator = LinkHeaderPagination()
            paginator.paginate_queryset(queryset, request)

    def test_get_paginated_response_first_page(self):
        # Given
        page_size, url = api_settings.PAGE_SIZE, '/api/pages/'
        request = self.factory.get(url)
        queryset = list(range(page_size + 1))
        expected = queryset[:page_size]

        # When
        paginator = LinkHeaderPagination()
        data = paginator.paginate_queryset(queryset, request)
        response = paginator.get_paginated_response(data)

        # Then
        self.assertListEqual(response.data, expected)
        self.assertIn('rel=\"next\"', response['Link'])
        self.assertIn('rel=\"last\"', response['Link'])
        self.assertNotIn('rel=\"first\"', response['Link'])
        self.assertNotIn('rel=\"prev\"', response['Link'])

    def test_get_paginated_response_middle_page(self):
        # Given
        page, page_size, url = 2, 5, '/api/pages/'
        request = self.factory.get(url, {'page': page, 'page_size': page_size})
        queryset = list(range(page_size * 3))
        expected = queryset[page_size:page_size+page_size]

        # When
        paginator = LinkHeaderPagination()
        data = paginator.paginate_queryset(queryset, request)
        response = paginator.get_paginated_response(data)

        # Then
        self.assertListEqual(response.data, expected)
        self.assertIn('rel=\"next\"', response['Link'])
        self.assertIn('rel=\"last\"', response['Link'])
        self.assertIn('rel=\"first\"', response['Link'])
        self.assertIn('rel=\"prev\"', response['Link'])

    def test_get_paginated_response_last_page(self):
        # Given
        page, page_size, url = 2, api_settings.PAGE_SIZE, '/api/pages/'
        request = self.factory.get(url, {'page': page})
        queryset = list(range(page_size + 1))
        expected = queryset[page_size:]

        # When
        paginator = LinkHeaderPagination()
        data = paginator.paginate_queryset(queryset, request)
        response = paginator.get_paginated_response(data)

        # Then
        self.assertListEqual(response.data, expected)
        self.assertNotIn('rel=\"next\"', response['Link'])
        self.assertNotIn('rel=\"last\"', response['Link'])
        self.assertIn('rel=\"first\"', response['Link'])
        self.assertIn('rel=\"prev\"', response['Link'])
