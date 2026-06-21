import asyncio

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from apps.accounts.faker.data import FakeUser
from apps.accounts.models import User
from apps.core.base_test_case import BaseTestCase
from apps.main import app
from apps.products.faker.data import FakeProduct
from apps.products.services import ProductService
from config.database import DatabaseManager


class ProductTestBase(BaseTestCase):
    product_endpoint = '/products/'

    # --- members ---
    admin: User | None = None
    admin_authorization = {}

    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)

        # Initialize the test database and session before the test class starts
        DatabaseManager.create_test_database()

        # --- create an admin ---
        cls.admin, access_token = FakeUser.populate_admin()
        cls.admin_authorization = {"Authorization": f"Bearer {access_token}"}

    @classmethod
    def teardown_class(cls):
        # Drop the test database after all tests in the class have finished
        DatabaseManager.drop_all_tables()


class TestCreateProduct(ProductTestBase):


    def test_access_permission(self):

        # TODO admin permission can access to all CRUD of a product also list of products
        # TODO non admin users only can use read a product or read a list of products if it status is
        #  'active or archive'
        ...

    def test_create_product(self):

        # --- request ---
        payload = FakeProduct.get_payload()
        response = self.client.post(self.product_endpoint, json=payload, headers=self.admin_authorization)
        assert response.status_code == status.HTTP_201_CREATED

        # --- response data ---
        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        # --- product ---
        assert expected['product_id'] > 0
        assert expected['product_name'] == payload['product_name']
        assert expected['description'] == payload['description']
        assert expected['status'] == payload['status']
        assert expected['updated_at'] is None
        assert expected['published_at'] is None
        self.assert_datetime_format(expected['created_at'])

        # --- options $ media ---
        assert expected['options'] is None
        assert expected['media'] is None

        # --- variants ---
        assert isinstance(expected['variants'], list)
        assert len(expected['variants']) == 1
        variant = expected['variants'][0]
        assert variant['variant_id'] > 0
        assert variant['product_id'] > 0
        assert variant['price'] == payload['price']
        assert variant['stock'] == payload['stock']
        assert variant['option1'] is None
        assert variant['option2'] is None
        assert variant['option3'] is None
        assert variant['updated_at'] is None
        self.assert_datetime_format(expected['created_at'])

    def test_create_product_with_options(self):


        # --- request ---
        payload = FakeProduct.get_payload_with_options()
        response = self.client.post(self.product_endpoint, json=payload, headers=self.admin_authorization)
        assert response.status_code == status.HTTP_201_CREATED

        # --- response data ---
        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        # --- product ---
        assert expected['product_id'] > 0
        assert expected['product_name'] == payload['product_name']
        assert expected['description'] == payload['description']
        assert expected['status'] == payload['status']
        assert expected['updated_at'] is None
        assert expected['published_at'] is None
        self.assert_datetime_format(expected['created_at'])

        # --- options ---
        assert isinstance(expected['options'], list)
        assert len(expected['options']) == 3
        for option in expected['options']:
            assert isinstance(option["options_id"], int)
            assert isinstance(option["option_name"], str)
            assert isinstance(option['items'], list)
            assert len(option['items']) == 2
            for item in option['items']:
                assert isinstance(item["item_id"], int)
                assert isinstance(item["item_name"], str)

        # --- variants ---
        assert isinstance(expected['variants'], list)
        assert len(expected['variants']) == 8
        for variant in expected['variants']:
            assert isinstance(variant["variant_id"], int)
            assert isinstance(variant["product_id"], int)
            assert isinstance(variant['price'], float)
            assert isinstance(variant['stock'], int)
            assert isinstance(variant['option1'], int)
            assert isinstance(variant['option2'], int)
            assert isinstance(variant['option3'], int)
            assert variant['updated_at'] is None
            self.assert_datetime_format(variant['created_at'])

        # --- media ---
        assert expected['media'] is None

    def test_create_product_required(self):

        # --- request ---
        payload = {
            'product_name': 'Test Product'
        }
        response = self.client.post(self.product_endpoint, json=payload, headers=self.admin_authorization)
        assert response.status_code == status.HTTP_201_CREATED

        # --- response data ---
        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        # --- product ---
        assert expected['product_id'] > 0
        assert expected['product_name'] == payload['product_name']
        assert expected['description'] is None
        assert expected['status'] == 'draft'
        assert expected['updated_at'] is None
        assert expected['published_at'] is None
        self.assert_datetime_format(expected['created_at'])

        # --- options & media ---
        assert expected['options'] is None
        assert expected['media'] is None

        # --- variants ---
        assert isinstance(expected['variants'], list)
        assert len(expected['variants']) == 1
        variant = expected['variants'][0]
        assert variant['variant_id'] > 0
        assert variant['product_id'] > 0
        assert variant['price'] == 0
        assert variant['stock'] == 0
        assert variant['option1'] is None
        assert variant['option2'] is None
        assert variant['option3'] is None
        assert variant['updated_at'] is None
        self.assert_datetime_format(expected['created_at'])

    def test_create_product_with_required_options(self):


        # --- request ---
        payload = {
            "product_name": "Test Product",
            "options": [
                {
                    "option_name": "color",
                    "items": ["red"]
                }
            ]
        }
        response = self.client.post(self.product_endpoint, json=payload, headers=self.admin_authorization)
        assert response.status_code == status.HTTP_201_CREATED

        # --- response data ---
        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        # --- product ---
        assert expected['product_id'] > 0
        assert expected['product_name'] == 'Test Product'
        assert expected['description'] is None
        assert expected['status'] == 'draft'
        assert expected['updated_at'] is None
        assert expected['published_at'] is None
        self.assert_datetime_format(expected['created_at'])

        # --- options ---
        assert isinstance(expected['options'], list)
        assert len(expected['options']) == 1
        for option in expected['options']:
            assert isinstance(option["options_id"], int)
            assert option["option_name"] == 'color'
            assert isinstance(option['items'], list)
            assert len(option['items']) == 1
            for item in option['items']:
                assert isinstance(item["item_id"], int)
                assert item["item_name"] == 'red'

        # --- variants ---
        assert isinstance(expected['variants'], list)
        assert len(expected['variants']) == 1
        for variant in expected['variants']:
            assert isinstance(variant["variant_id"], int)
            assert isinstance(variant["product_id"], int)
            assert isinstance(variant['price'], float)
            assert isinstance(variant['stock'], int)
            assert isinstance(variant['option1'], int)
            assert variant['option2'] is None
            assert variant['option3'] is None
            assert variant['updated_at'] is None
            self.assert_datetime_format(variant['created_at'])

        # --- media ---
        assert expected['media'] is None

    # ---------------------
    # --- Test Payloads ---
    # ---------------------

    # TODO test_with_html_description

    def test_payload_is_empty(self):


        response = self.client.post(self.product_endpoint, json={}, headers=self.admin_authorization)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_payload_product_name_max_length(self):


        payload = {
            'product_name': 'T' * 256
        }

        response = self.client.post(self.product_endpoint, json=payload, headers=self.admin_authorization)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("name", ["", None])
    def test_payload_product_name_invalid(self, name):


        payload = {
            'product_name': name
        }

        response = self.client.post(self.product_endpoint, json=payload, headers=self.admin_authorization)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_payload_without_product_name(self):


        payload = {
            'description': 'blob'
        }

        response = self.client.post(self.product_endpoint, json=payload, headers=self.admin_authorization)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("status_value", ["", None, "blob", 1, False, 'active', 'archived', 'draft'])
    def test_payload_invalid_status(self, status_value):


        payload = {
            'product_name': 'Test Product',
            'status': status_value
        }

        # Handle different status_value cases
        if status_value not in ['active', 'archived', 'draft']:
            expected_status = 'draft'
        else:
            expected_status = status_value

        # --- request ---
        response = self.client.post(self.product_endpoint, json=payload, headers=self.admin_authorization)

        # --- expected ---
        if isinstance(status_value, str | None):
            assert response.status_code == status.HTTP_201_CREATED
            expected = response.json().get('product')
            assert expected['status'] == expected_status
        else:
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("options_value", [
        '', [''], ['blob'], [{}],
        [{'option_name': []}],
        [{'option_name': ''}],
        [{'option_name': '', 'items': []}],
        [{'option_name': '', 'items': ['a']}],
        [{'option_name': 'blob', 'items': ''}],
        [{'option_name': 'blob', 'items': [1]}],
        [{'option_name': 'blob', 'items_blob': ["a"]}],
        [{'option_blob': 'blob', 'items': ['a']}],
        [{'items': ['a'], 'option_blob': 'blob'}],
        [{'option_name': 'blob', 'items': [["a", "b"]]}]
    ])
    def test_payload_invalid_options(self, options_value):


        payload = {
            'product_name': 'Test Product',
            'options': options_value
        }

        response = self.client.post(self.product_endpoint, json=payload, headers=self.admin_authorization)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("price_value", [-10, None, ""])
    def test_payload_invalid_price(self, price_value):


        payload = {
            'product_name': 'Test Product',
            'price': price_value
        }

        response = self.client.post(self.product_endpoint, json=payload, headers=self.admin_authorization)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("stock_value", [-10, None, "", 1.3])
    def test_payload_invalid_stock(self, stock_value):


        payload = {
            'product_name': 'Test Product',
            'stock': stock_value
        }

        response = self.client.post(self.product_endpoint, json=payload, headers=self.admin_authorization)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_payload_with_duplicate_options(self):


        payload = {
            "product_name": 'blob',
            "options": [
                {
                    "option_name": "color",
                    "items": ["red"]
                },
                {
                    "option_name": "size",
                    "items": ["small"]
                },
                {
                    "option_name": "color",
                    "items": ["blue"]
                }
            ]
        }
        response = self.client.post(self.product_endpoint, json=payload, headers=self.admin_authorization)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_payload_with_duplicate_items_in_options(self):


        payload = {
            "product_name": "blob",
            "options": [
                {
                    "option_name": "color",
                    "items": ["red", "blue", "red"]
                },
                {
                    "option_name": "size",
                    "items": ["S", "L"]
                }
            ]
        }
        response = self.client.post(self.product_endpoint, json=payload, headers=self.admin_authorization)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_payload_with_max_3_options(self):


        payload = {
            "product_name": "blob",
            "options": [
                {
                    "option_name": "color",
                    "items": ["red"]
                },
                {
                    "option_name": "size",
                    "items": ["small"]
                },
                {
                    "option_name": "material",
                    "items": ["x1", "x2"]
                },
                {
                    "option_name": "blob",
                    "items": ["b"]
                }
            ]
        }

        response = self.client.post(self.product_endpoint, json=payload, headers=self.admin_authorization)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestRetrieveProduct(ProductTestBase):


    def test_retrieve_product(self):


        # --- create a product ---
        payload, product = FakeProduct.populate_product()

        # --- retrieve product ---
        response = self.client.get(f'{self.product_endpoint}{product.id}')
        assert response.status_code == status.HTTP_200_OK

        # --- response data ---
        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        # --- product ---
        assert expected['product_id'] == product.id
        assert expected['product_name'] == payload['product_name']
        assert expected['description'] == payload['description']
        assert expected['status'] == payload['status']
        assert expected['updated_at'] is None
        assert expected['published_at'] is None
        self.assert_datetime_format(expected['created_at'])

        # --- options & media ---
        assert expected['options'] is None
        assert expected['media'] is None

        # --- variant ---
        assert isinstance(expected['variants'], list)
        assert len(expected['variants']) == 1
        variant = expected['variants'][0]
        assert variant['variant_id'] > 0
        assert variant['product_id'] == product.id
        assert variant['price'] == payload['price']
        assert variant['stock'] == payload['stock']
        assert variant['option1'] is None
        assert variant['option2'] is None
        assert variant['option3'] is None
        assert variant['updated_at'] is None
        self.assert_datetime_format(expected['created_at'])

    def test_retrieve_product_with_options(self):


        # --- create a product ---
        payload, product = FakeProduct.populate_product_with_options()

        # --- retrieve product ---
        response = self.client.get(f"{self.product_endpoint}{product.id}")
        assert response.status_code == status.HTTP_200_OK

        # --- response data ---
        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        # --- product ---
        assert expected['product_id'] == product.id
        assert expected['product_name'] == payload['product_name']
        assert expected['description'] == payload['description']
        assert expected['status'] == payload['status']
        assert expected['updated_at'] is None
        assert expected['published_at'] is None
        self.assert_datetime_format(expected['created_at'])

        # --- options ---
        assert isinstance(expected['options'], list)
        assert len(expected['options']) == 3
        for option in expected['options']:
            assert isinstance(option["options_id"], int)
            assert isinstance(option["option_name"], str)
            assert isinstance(option['items'], list)
            assert len(option['items']) == 2
            for item in option['items']:
                assert isinstance(item["item_id"], int)
                assert isinstance(item["item_name"], str)

        # --- variants ---
        assert isinstance(expected['variants'], list)
        assert len(expected['variants']) == 8
        for variant in expected['variants']:
            assert isinstance(variant["variant_id"], int)
            assert variant["product_id"] == product.id
            assert isinstance(variant['price'], float)
            assert isinstance(variant['stock'], int)
            assert isinstance(variant['option1'], int)
            assert isinstance(variant['option2'], int)
            assert isinstance(variant['option3'], int)
            assert variant['updated_at'] is None
            self.assert_datetime_format(variant['created_at'])

        # --- media ---
        assert expected['media'] is None

    def test_retrieve_product_with_media(self):

        # --- create a product ---
        payload, product = asyncio.run(FakeProduct.populate_product_with_media())

        # --- retrieve product ---
        response = self.client.get(f"{self.product_endpoint}{product.id}")
        assert response.status_code == status.HTTP_200_OK

        # --- response data ---
        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        # --- product ---
        assert expected['product_id'] == product.id
        assert expected['product_name'] == payload['product_name']
        assert expected['description'] == payload['description']
        assert expected['status'] == payload['status']
        assert expected['updated_at'] is None
        assert expected['published_at'] is None
        self.assert_datetime_format(expected['created_at'])

        # --- options ---
        assert expected['options'] is None

        # --- variant ---
        assert isinstance(expected['variants'], list)
        assert len(expected['variants']) == 1
        variant = expected['variants'][0]
        assert variant['variant_id'] > 0
        assert variant['product_id'] == product.id
        assert variant['price'] == payload['price']
        assert variant['stock'] == payload['stock']
        assert variant['option1'] is None
        assert variant['option2'] is None
        assert variant['option3'] is None
        assert variant['updated_at'] is None
        self.assert_datetime_format(expected['created_at'])

        # --- media ---
        assert isinstance(expected['media'], list)
        assert len(expected['media']) > 0
        media = expected['media']
        for media_item in media:
            assert media_item["media_id"] > 0
            assert media_item["product_id"] > 0
            assert media_item["alt"] == payload['alt']
            assert media_item["src"] is not None
            assert media_item["type"] is not None
            assert media_item["updated_at"] is None
            self.assert_datetime_format(media_item['created_at'])

    def test_retrieve_product_with_options_media(self):

        # --- create a product ---
        payload, product = asyncio.run(FakeProduct.populate_product_with_options_media())

        # --- retrieve product ---
        response = self.client.get(f"{self.product_endpoint}{product.id}")
        assert response.status_code == status.HTTP_200_OK

        # --- response data ---
        expected = response.json()
        assert isinstance(expected['product'], dict)
        expected = expected['product']

        # --- product ---
        assert expected['product_id'] == product.id
        assert expected['product_name'] == payload['product_name']
        assert expected['description'] == payload['description']
        assert expected['status'] == payload['status']
        assert expected['updated_at'] is None
        assert expected['published_at'] is None
        self.assert_datetime_format(expected['created_at'])

        # --- options ---
        assert isinstance(expected['options'], list)
        assert len(expected['options']) == 3
        for option in expected['options']:
            assert isinstance(option["options_id"], int)
            assert isinstance(option["option_name"], str)
            assert isinstance(option['items'], list)
            assert len(option['items']) == 2
            for item in option['items']:
                assert isinstance(item["item_id"], int)
                assert isinstance(item["item_name"], str)

        # --- variants ---
        assert isinstance(expected['variants'], list)
        assert len(expected['variants']) == 8
        for variant in expected['variants']:
            assert isinstance(variant["variant_id"], int)
            assert variant["product_id"] == product.id
            assert isinstance(variant['price'], float)
            assert isinstance(variant['stock'], int)
            assert isinstance(variant['option1'], int)
            assert isinstance(variant['option2'], int)
            assert isinstance(variant['option3'], int)
            assert variant['updated_at'] is None
            self.assert_datetime_format(variant['created_at'])

        # --- media ---
        assert isinstance(expected['media'], list)
        assert len(expected['media']) > 0
        media = expected['media']
        for media_item in media:
            assert media_item["media_id"] > 0
            assert media_item["product_id"] > 0
            assert media_item["alt"] == payload['alt']
            assert media_item["src"] is not None
            assert media_item["type"] is not None
            assert media_item["updated_at"] is None
            self.assert_datetime_format(media_item['created_at'])

    def test_retrieve_product_404(self):

        response = self.client.get(f"{self.product_endpoint}{999999999}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # ---------------------
    # --- Test Payloads ---
    # ---------------------



class TestListProduct(ProductTestBase):

    def test_list_products_no_content(self):


        response = self.client.get(self.product_endpoint)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_list_products(self):

        # --- create 30 products ---
        asyncio.run(FakeProduct.populate_30_products())

        # --- request ---
        response = self.client.get(self.product_endpoint)
        assert response.status_code == status.HTTP_200_OK

        # --- response data ---
        expected = response.json().get('products')
        assert isinstance(expected, list)
        assert len(expected) == 12

        for product in expected:
            assert len(product) == 10
            assert isinstance(product['product_id'], int)
            assert isinstance(product['product_name'], str)




class TestUpdateProduct(ProductTestBase):

    @pytest.mark.parametrize("update_payload", [
        {"product_name": "updated name"},
        {"description": "updated description"},
        {"status": "archived"},
        {"product_name": "updated name", "description": "updated description"},
        {"product_name": "updated name", "status": "draft"},
        {"description": "updated description", "status": "archived"}
    ])
    def test_update_product(self, update_payload):
        """
        Test update a product, only update fields that are there in request body and leave other fields unchanging.
        """

        # --- create product ---
        payload, product = FakeProduct.populate_product()

        response = self.client.put(f"{self.product_endpoint}{product.id}", json=update_payload,
                                   headers=self.admin_authorization)
        assert response.status_code == status.HTTP_200_OK

        expected = response.json().get('product')
        self.assert_datetime_format(expected['updated_at'])

        # `created_at` should be same as before the update
        assert expected['created_at'] == self.convert_datetime_to_string(product.created_at)

        # ----------------------
        # --- product fields ---
        # ----------------------

        field = tuple(update_payload.keys())
        match field:
            case ('product_name', ):
                assert expected['product_name'] == update_payload['product_name']
                assert expected['description'] == product.description
                assert expected['status'] == product.status

            case ('description', ):
                assert expected['product_name'] == product.product_name
                assert expected['description'] == update_payload['description']
                assert expected['status'] == product.status

            case ('status', ):
                assert expected['product_name'] == product.product_name
                assert expected['description'] == product.description
                assert expected['status'] == update_payload['status']

            case ('product_name', 'description'):
                assert expected['product_name'] == update_payload['product_name']
                assert expected['description'] == update_payload['description']
                assert expected['status'] == product.status

            case ('product_name', 'status'):
                assert expected['product_name'] == update_payload['product_name']
                assert expected['description'] == product.description
                assert expected['status'] == update_payload['status']

            case ('description', 'status'):
                assert expected['product_name'] == product.product_name
                assert expected['description'] == update_payload['description']
                assert expected['status'] == update_payload['status']

            case _:
                # To ensure that all case statements in my code are executed
                raise ValueError(f"Unknown field(s): {field}")

    # ---------------------
    # --- Test Payloads ---
    # ---------------------


class TestDestroyProduct(ProductTestBase):


    def test_delete_product(self):


        # --- create a product ---
        _, product = FakeProduct.populate_product()

        # --- request ---
        response = self.client.delete(f"{self.product_endpoint}{product.id}", headers=self.admin_authorization)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # --- expected ---
        expected = self.client.get(f"{self.product_endpoint}{product.id}")
        assert expected.status_code == status.HTTP_404_NOT_FOUND

        variant = ProductService.retrieve_variants(product.id)
        assert variant is None

    @pytest.mark.asyncio
    async def test_delete_product_with_media(self):


        # --- create a product with media ---
        _, product = await FakeProduct.populate_product_with_media()

        # --- request ---
        response = self.client.delete(f"{self.product_endpoint}{product.id}", headers=self.admin_authorization)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # --- expected ---
        expected = self.client.get(f"{self.product_endpoint}{product.id}")
        assert expected.status_code == status.HTTP_404_NOT_FOUND

        variant = ProductService.retrieve_variants(product.id)
        assert variant is None

        media = ProductService.retrieve_media_list(product.id)
        assert media is None

    def test_delete_product_with_options(self):


        # --- create a product with options ---
        _, product = FakeProduct.populate_product_with_options()

        # --- request ---
        response = self.client.delete(f"{self.product_endpoint}{product.id}", headers=self.admin_authorization)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # --- expected ---
        expected = self.client.get(f"{self.product_endpoint}{product.id}")
        assert expected.status_code == status.HTTP_404_NOT_FOUND

        variant = ProductService.retrieve_variants(product.id)
        assert variant is None

        options = ProductService.retrieve_options(product.id)
        assert options is None

    @pytest.mark.asyncio
    async def test_delete_product_with_options_media(self):


        # --- create a product with options and media ---
        _, product = await FakeProduct.populate_product_with_options_media()

        # --- request ---
        response = self.client.delete(f"{self.product_endpoint}{product.id}", headers=self.admin_authorization)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # --- expected ---
        expected = self.client.get(f"{self.product_endpoint}{product.id}")
        assert expected.status_code == status.HTTP_404_NOT_FOUND

        variant = ProductService.retrieve_variants(product.id)
        assert variant is None

        options = ProductService.retrieve_options(product.id)
        assert options is None

        media = ProductService.retrieve_media_list(product.id)
        assert media is None

