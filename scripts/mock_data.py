"""Mock data generator for Furniture Shop"""

import json
from datetime import datetime, timedelta
import random

# Mock Customers
CUSTOMERS = [
    {
        "id": "customer_001",
        "name": "John Smith",
        "email": "john.smith@email.com",
        "phone": "+1-555-0101"
    },
    {
        "id": "customer_002", 
        "name": "Sarah Johnson",
        "email": "sarah.johnson@email.com",
        "phone": "+1-555-0102"
    },
    {
        "id": "customer_003",
        "name": "Michael Brown",
        "email": "michael.brown@email.com", 
        "phone": "+1-555-0103"
    },
    {
        "id": "customer_004",
        "name": "Emily Davis",
        "email": "emily.davis@email.com",
        "phone": "+1-555-0104"
    },
    {
        "id": "customer_005",
        "name": "David Wilson",
        "email": "david.wilson@email.com",
        "phone": "+1-555-0105"
    }
]

# Mock Products
PRODUCTS = [
    {
        "id": "FURN-001",
        "name": "Modern Leather Sofa",
        "category": "Living Room",
        "price": 1299.99
    },
    {
        "id": "FURN-002", 
        "name": "Dining Table Set",
        "category": "Dining Room",
        "price": 899.99
    },
    {
        "id": "FURN-003",
        "name": "Queen Size Bed Frame",
        "category": "Bedroom", 
        "price": 599.99
    },
    {
        "id": "FURN-004",
        "name": "Office Desk",
        "category": "Office",
        "price": 399.99
    },
    {
        "id": "FURN-005",
        "name": "Coffee Table",
        "category": "Living Room",
        "price": 249.99
    },
    {
        "id": "FURN-006",
        "name": "Bookshelf",
        "category": "Living Room",
        "price": 199.99
    },
    {
        "id": "FURN-007",
        "name": "Leather Armchair",
        "category": "Living Room",
        "price": 499.99
    },
    {
        "id": "FURN-008",
        "name": "Dining Chairs Set",
        "category": "Dining Room",
        "price": 399.99
    },
    {
        "id": "FURN-009",
        "name": "Nightstand",
        "category": "Bedroom",
        "price": 149.99
    },
    {
        "id": "FURN-010",
        "name": "TV Stand",
        "category": "Living Room",
        "price": 349.99
    }
]

# Generate Mock Orders
def generate_orders(num_orders=30):
    orders = []
    for i in range(num_orders):
        order_id = f"ORD-{1000 + i:03d}"
        customer = random.choice(CUSTOMERS)
        
        # Random order date in the past 90 days
        order_date = datetime.now() - timedelta(days=random.randint(1, 90))
        
        # Delivery date typically 7-21 days after order
        delivery_days = random.randint(7, 21)
        delivery_date = order_date + timedelta(days=delivery_days)
        
        # Random number of products (1-5 per order, more realistic distribution)
        num_products = random.randint(1, 5)
        # Weight the selection so some products are more common
        product_selection = []
        for _ in range(num_products):
            # Higher chance for popular items
            if random.random() > 0.3:
                product_selection.append(random.choice(PRODUCTS[:6]))  # First 6 are more popular
            else:
                product_selection.append(random.choice(PRODUCTS))
        
        # Calculate total
        total = sum(product["price"] for product in product_selection)
        
        orders.append({
            "id": order_id,
            "customer": customer,
            "products": product_selection,
            "order_date": order_date.strftime("%Y-%m-%d"),
            "delivery_date": delivery_date.strftime("%Y-%m-%d"),
            "total": total,
            "status": random.choice(["delivered", "delivered", "delivered", "in_transit", "processing"])  # Mostly delivered
        })
    
    return orders

def save_mock_data():
    """Save mock data to JSON files in frontend accessible location"""
    orders = generate_orders()
    
    mock_data = {
        "customers": CUSTOMERS,
        "products": PRODUCTS,
        "orders": orders
    }
    
    # Save for backend reference
    with open("mock_data.json", "w") as f:
        json.dump(mock_data, f, indent=2)
    
    # Save simplified version for frontend
    frontend_mock_data = {
        "customers": [{"id": c["id"], "name": c["name"], "email": c["email"]} for c in CUSTOMERS],
        "products": [{"id": p["id"], "name": p["name"], "category": p["category"]} for p in PRODUCTS],
        "customerOrders": {}
    }
    
    # Organize orders by customer for easy frontend dropdowns
    for order in orders:
        customer_id = order["customer"]["id"]
        if customer_id not in frontend_mock_data["customerOrders"]:
            frontend_mock_data["customerOrders"][customer_id] = []
        frontend_mock_data["customerOrders"][customer_id].append({
            "orderId": order["id"],
            "products": [{"id": p["id"], "name": p["name"]} for p in order["products"]],
            "deliveryDate": order["delivery_date"],
            "status": order["status"]
        })
    
    # Save frontend mock data
    with open("../frontend/src/data/mock_data.json", "w") as f:
        json.dump(frontend_mock_data, f, indent=2)
    
    print(f"Mock data saved to mock_data.json and frontend/src/data/mock_data.json")
    print(f"Generated {len(CUSTOMERS)} customers")
    print(f"Generated {len(PRODUCTS)} products") 
    print(f"Generated {len(orders)} orders")

if __name__ == "__main__":
    save_mock_data()