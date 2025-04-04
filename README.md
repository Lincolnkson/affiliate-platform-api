# Affiliate Marketing Platform

A comprehensive affiliate marketing platform built with Django REST Framework and MySQL. This platform connects vendors, affiliates, and customers in an efficient ecosystem.

## Features

- **User Management**: Registration and authentication for vendors, affiliates, and admins
- **Vendor Management**: Product creation and management
- **Affiliate Management**: Affiliate code tracking and earnings calculation
- **Product Management**: Full CRUD operations for products and categories
- **Review System**: Customer reviews and ratings for products

## Technology Stack

- **Framework**: Django REST Framework
- **Database**: MySQL
- **Authentication**: Token Authentication

## Project Setup

### Prerequisites

- Python 3.8+
- MySQL Server
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/affiliate-platform.git
   cd affiliate-platform
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root directory by copying from `.env.example`:
   ```bash
   cp .env.example .env
   ```
   
   Then fill out the values:
   ```
   ENGINE=django.db.backends.mysql
   NAME=affiliate_db
   USER=your_mysql_username
   PASSWORD=your_mysql_password
   HOST=localhost
   PORT=3306
   
   SECRET_KEY=your-secret-key-goes-here
   DEBUG=True
   ```

5. Create MySQL database:
   ```sql
   CREATE DATABASE affiliate_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

6. Apply migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. Create a superuser (admin):
   ```bash
   python manage.py createsuperuser
   ```

8. Run the development server:
   ```bash
   python manage.py runserver
   ```

9. Access the API at `http://localhost:8000/` and admin panel at `http://localhost:8000/admin/`

## Project Structure

- `models.py`: Contains all database models (User, Vendor, Affiliate, Product, etc.)
- `serializers.py`: Contains serializers for API data validation and conversion
- `views.py`: Contains API views and viewsets
- `permissions.py`: Custom permission classes for user access control
- `urls.py`: API routing configuration
- `admin.py`: Admin panel configuration

## User Types

The platform supports three user types:
- **Vendor**: Can create and manage products
- **Affiliate**: Can generate affiliate codes and earn commissions
- **Admin**: Has access to all platform features and user management

## API Endpoints

### Authentication Endpoints
- `POST /auth/register/` - Register a new user
- `POST /auth/register/vendor/` - Register a vendor
- `POST /auth/register/affiliate/` - Register an affiliate
- `POST /auth/login/` - Get authentication token
- `GET/PUT /auth/profile/` - View/update user profile

### Vendor Endpoints
- `GET /vendors/` - List all vendors
- `GET /vendors/{id}/` - Get vendor details
- `PUT /vendors/{id}/` - Update vendor information
- `GET /vendors/{id}/products/` - Get vendor products

### Product Endpoints
- `GET /products/` - List all products
- `POST /products/` - Create a new product (vendor only)
- `GET /products/{id}/` - Get product details
- `PUT /products/{id}/` - Update product (product owner only)
- `DELETE /products/{id}/` - Delete product (product owner only)
- `POST /products/{id}/add_category/` - Add product category
- `PATCH /products/{id}/update-product/` - Update specific product fields
- `DELETE /products/{id}/delete-product/` - Delete a product

### Review Endpoints
- `GET /products/{id}/reviews/` - Get product reviews
- `POST /products/{id}/reviews/` - Add product review
- `PUT /products/{id}/reviews/{reviewId}/` - Update review (author only)
- `DELETE /products/{id}/reviews/{reviewId}/` - Delete review (author only)

### Affiliate Endpoints
- `GET /affiliates/` - List all affiliates
- `GET /affiliates/{id}/` - Get affiliate details
- `PUT /affiliates/{id}/` - Update affiliate information

## Permission System

The platform implements a custom permission system:
- `IsVendor`: Only vendors can access
- `IsAffiliate`: Only affiliates can access
- `IsAdmin`: Only admins can access
- `IsProductOwner`: Only the product owner can modify the product
- `IsReviewAuthor`: Only the review author can modify the review

## Example Usage

### Register a Vendor
```bash
curl -X POST http://localhost:8000/auth/register/vendor/ \
  -H "Content-Type: application/json" \
  -d '{
    "user": {
      "email": "vendor@example.com",
      "password": "secure_password",
      "password2": "secure_password",
      "first_name": "John",
      "last_name": "Doe"
    },
    "company_name": "ABC Store"
  }'
```

### Login and Get Token
```bash
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "vendor@example.com",
    "password": "secure_password"
  }'
```

### Create a Product (as Vendor)
```bash
curl -X POST http://localhost:8000/products/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -d '{
    "name": "Awesome Product",
    "description": "This is an amazing product",
    "price": 99.99,
    "status": "in_stock"
  }'
```

## Future Enhancements

1. Implement payment gateway integration
2. Add analytics dashboard for vendors and affiliates
3. Implement email notifications for order status updates
4. Add product image upload functionality
5. Implement a commission calculation system

## Contributors

- Lincoln (lincolnmotlalepula@gmail.com)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
