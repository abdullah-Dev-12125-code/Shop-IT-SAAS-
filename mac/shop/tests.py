import json
from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse

from .models import Order, Product


class ShopUrlTests(TestCase):
	def test_shop_checkout_url_resolves(self):
		self.assertEqual(reverse("shop:checkout"), "/shop/checkout/")

	def test_shop_create_order_url_resolves(self):
		self.assertEqual(reverse("shop:create-order"), "/shop/api/create-order/")


class CartOrderTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.product = Product.objects.create(
			product_name="Test Product",
			category="Test",
			sub_category="Test",
			price=199,
			desc="A test product",
			available_now=1,
		)

	def test_create_order_persists_normalized_cart(self):
		payload = {
			"first_name": "Ada",
			"last_name": "Lovelace",
			"email": "ada@example.com",
			"phone": "1234567890",
			"address": "1 Logic Lane",
			"city": "London",
			"zip_code": "SW1A 1AA",
			"country": "UK",
			"payment_method": "cod",
			"total_price": 0,
			"cart": [
				{
					"id": self.product.id,
					"name": "Ignored Name",
					"price": 1,
					"qty": 2,
					"image": "",
				}
			],
		}

		response = self.client.post(
			reverse("shop:create-order"),
			data=json.dumps(payload),
			content_type="application/json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()["success"], True)
		self.assertEqual(response.json()["total_price"], "398.00")

		order = Order.objects.get()
		self.assertEqual(order.total_price, Decimal("398.00"))
		self.assertIn("Test Product", order.item_json)
