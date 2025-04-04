from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .models import Vendor, Affiliate, Product, Review

User = get_user_model()

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'account_type': 'admin'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.token = Token.objects.create(user=self.user)
    
    def test_user_registration(self):
        url = reverse('register')
        data = {
            'email': 'new@example.com',
            'password': 'newpass123',
            'password2': 'newpass123',
            'account_type': 'affiliate',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_user_login(self):
        url = reverse('login')
        data = {
            'username': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

class VendorTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='vendor@test.com',
            password='testpass123',
            account_type='vendor'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.vendor = Vendor.objects.create(user=self.user, company_name='Test Vendor')

    def test_create_vendor(self):
        url = reverse('register-vendor')
        data = {
            'user': {
                'email': 'newvendor@test.com',
                'password': 'vendorpass123',
                'password2': 'vendorpass123',
                'account_type': 'vendor',
                'first_name': 'Vendor',
                'last_name': 'User'
            },
            'company_name': 'New Vendor'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vendor.objects.count(), 2)

    def test_get_vendor(self):
        url = reverse('vendor-detail', args=[self.vendor.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], 'Test Vendor')

class ProductTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='vendor@test.com',
            password='testpass123',
            account_type='vendor'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.vendor = Vendor.objects.create(user=self.user, company_name='Test Vendor')
        self.product = Product.objects.create(
            vendor=self.vendor,
            name='Test Product',
            description='Test Description',
            price=9.99,
            status='in_stock'
        )

    def test_create_product(self):
        url = reverse('product-list')
        data = {
            'name': 'New Product',
            'description': 'New Description',
            'price': 19.99,
            'status': 'in_stock'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_get_products(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_add_product_category(self):
        url = reverse('product-add-category', args=[self.product.id])
        data = {'category': 'Electronics'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.product.categories.count(), 1)

class ReviewTests(APITestCase):
    def setUp(self):
        # Create vendor and product
        self.vendor_user = User.objects.create_user(
            email='vendor@test.com',
            password='testpass123',
            account_type='vendor'
        )
        self.vendor = Vendor.objects.create(user=self.vendor_user, company_name='Test Vendor')
        self.product = Product.objects.create(
            vendor=self.vendor,
            name='Test Product',
            description='Test Description',
            price=9.99,
            status='in_stock'
        )
        
        # Create affiliate user
        self.affiliate_user = User.objects.create_user(
            email='affiliate@test.com',
            password='testpass123',
            account_type='affiliate'
        )
        self.affiliate_token = Token.objects.create(user=self.affiliate_user)
        
        # Set affiliate credentials
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.affiliate_token.key)

    def test_create_review(self):
        url = reverse('product-reviews-list', args=[self.product.id])
        data = {
            'rating': 5,
            'text': 'Great product!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.first().rating, 5)

    def test_get_reviews(self):
        Review.objects.create(
            product=self.product,
            user=self.affiliate_user,
            rating=4,
            text='Good product'
        )
        url = reverse('product-reviews-list', args=[self.product.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
