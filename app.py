import os
import json
import uuid
from datetime import datetime
import pandas as pd
import streamlit as st

# ==================== PAGE CONFIGURATION ====================

st.set_page_config(
    page_title="Blossom Restaurant",
    page_icon="🌸",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")
ORDERS_FILE = os.path.join(BASE_DIR, "restaurant_data.json")

# ==================== MENU ====================

MENU = [
    {"id": 1, "name": "Veg Biryani", "price": 140, "category": "Biryani", "type": "Veg", "image": "veg_biryani.jpg", "desc": "Aromatic vegetable biryani with Indian spices."},
    {"id": 2, "name": "Chicken Dum Biryani", "price": 220, "category": "Biryani", "type": "Non-Veg", "image": "chicken_biryani.jpg", "desc": "Delicious chicken dum biryani."},
    {"id": 3, "name": "Paneer Butter Masala", "price": 180, "category": "Curry", "type": "Veg", "image": "paneer.jpg", "desc": "Paneer in creamy tomato butter gravy."},
    {"id": 4, "name": "Chicken Curry", "price": 200, "category": "Curry", "type": "Non-Veg", "image": "chicken_curry.jpg", "desc": "Traditional Indian chicken curry."},
    {"id": 5, "name": "Masala Dosa", "price": 90, "category": "Tiffins", "type": "Veg", "image": "masala_dosa.jpg", "desc": "Crispy dosa with potato masala."},
    {"id": 6, "name": "Veg Fried Rice", "price": 150, "category": "Rice", "type": "Veg", "image": "veg_fried_rice.jpg", "desc": "Fried rice with fresh vegetables."},
    {"id": 7, "name": "Chicken Fried Rice", "price": 190, "category": "Rice", "type": "Non-Veg", "image": "chicken_fried_rice.jpg", "desc": "Chicken fried rice with vegetables."},
    {"id": 8, "name": "Gulab Jamun", "price": 70, "category": "Desserts", "type": "Veg", "image": "gulab_jamun.jpg", "desc": "Sweet gulab jamun in sugar syrup."},
    {"id": 9, "name": "Fresh Lime Juice", "price": 50, "category": "Drinks", "type": "Veg", "image": "lime_juice.jpg", "desc": "Refreshing fresh lime juice."},
    {"id": 10, "name": "Butter Naan", "price": 40, "category": "Breads", "type": "Veg", "image": "butter_naan.jpg", "desc": "Soft naan topped with butter."},
    {"id": 11, "name": "Lime Soda", "price": 60, "category": "Drinks", "type": "Veg", "image": "lime_soda.jpg", "desc": "Refreshing chilled lime soda."}
]

STATUSES = [
    "Order Placed",
    "Preparing",
    "Out for Delivery",
    "Delivered",
    "Cancelled"
]

# ==================== ORDER STORAGE ====================

def normalize_order(order):
    """Support both old and new order formats."""
    order = dict(order)

    order["order_id"] = str(
        order.get("order_id") or order.get("id") or
        "BL" + uuid.uuid4().hex[:8].upper()
    )

    order["id"] = order["order_id"]
    order["customer"] = order.get("customer", "Customer")
    order["phone"] = order.get("phone", "")
    order["address"] = order.get("address", "")
    order["payment"] = order.get("payment", "Cash on Delivery")
    order["total"] = float(order.get("total", 0))
    order["status"] = order.get("status", "Order Placed")
    order["created_at"] = (
        order.get("created_at") or order.get("date") or
        datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    )
    order["date"] = order["created_at"]

    raw_items = order.get("items", [])
    items = []

    if isinstance(raw_items, dict):
        for name, quantity in raw_items.items():
            menu_item = next(
                (item for item in MENU if item["name"] == name), None
            )
            price = menu_item["price"] if menu_item else 0
            items.append({
                "name": name,
                "price": price,
                "quantity": int(quantity),
                "subtotal": price * int(quantity)
            })

    elif isinstance(raw_items, list):
        for item in raw_items:
            if isinstance(item, dict):
                name = item.get("name", "Unknown item")
                quantity = int(item.get("quantity", 1))
                menu_item = next(
                    (m for m in MENU if m["name"] == name), None
                )
                price = int(item.get(
                    "price", menu_item["price"] if menu_item else 0
                ))
                items.append({
                    "name": name,
                    "price": price,
                    "quantity": quantity,
                    "subtotal": price * quantity
                })

    order["items"] = items
    return order


def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []

    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            return []

        return [normalize_order(order) for order in data
                if isinstance(order, dict)]

    except (json.JSONDecodeError, OSError):
        return []


def save_orders():
    with open(ORDERS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            st.session_state.orders,
            file,
            indent=2,
            ensure_ascii=False
        )


# ==================== SESSION STATE ====================

if "cart" not in st.session_state:
    st.session_state.cart = {}

if "orders" not in st.session_state:
    st.session_state.orders = load_orders()

if "last_order" not in st.session_state:
    st.session_state.last_order = ""

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

# ==================== STYLING ====================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #fff8f5, #fff0f3);
    color: #49343c;
}
[data-testid="stHeader"] {
    background: #fff8f5;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #fff0f3, #fce1e8);
    border-right: 1px solid #f0c5d2;
}
[data-testid="stSidebar"] * {
    color: #702c45 !important;
}
.stApp h1, .stApp h2, .stApp h3 {
    color: #a33d60 !important;
    font-family: Georgia, serif;
}
.stApp p, .stApp label {
    color: #49343c;
}
.stApp input, .stApp textarea {
    background: white !important;
    color: #49343c !important;
    border: 1px solid #e8b8c8 !important;
    border-radius: 10px !important;
}
.stApp [data-baseweb="select"] > div {
    background: white !important;
    color: #49343c !important;
    border-radius: 10px !important;
}
.stButton > button, .stFormSubmitButton > button {
    background: linear-gradient(135deg, #b83260, #e45f83) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: bold !important;
    transition: 0.2s;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 14px #e8b8c8;
}
[data-testid="stImage"] img {
    border-radius: 16px;
    box-shadow: 0 5px 16px #ead1d9;
}
[data-testid="stExpander"] {
    background: #fffdfc;
    border: 1px solid #f0cbd6;
    border-radius: 14px;
}
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #f0cbd6;
    padding: 12px;
    border-radius: 14px;
}
[data-testid="stMetricValue"] {
    color: #922c50 !important;
}
.blossom-title {
    text-align: center;
    font-family: Georgia, serif;
    font-size: 42px;
    font-weight: 900;
    color: #a32250 !important;
    text-shadow: 2px 3px 5px #edc0d0;
    padding: 15px 0 5px;
}
.blossom-subtitle {
    text-align: center;
    font-family: Georgia, serif;
    font-size: 18px;
    font-style: italic;
    color: #84445a !important;
    margin-bottom: 25px;
}
</style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================

logo_path = os.path.join(IMAGE_DIR, "logo.png")

if os.path.isfile(logo_path):
    st.sidebar.image(logo_path, width=145)
else:
    st.sidebar.markdown(
        "<h2 style='color:#a32250 !important;'>🌸 Blossom</h2>",
        unsafe_allow_html=True
    )

st.sidebar.caption("Fresh food, happy moments")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    ["Home & Menu", "Cart & Checkout", "Track Order", "Admin Dashboard"]
)

st.sidebar.divider()
st.sidebar.write("📍 Hyderabad")
st.sidebar.write("🕒 10 AM – 10 PM")

# ==================== HOME AND MENU ====================

if page == "Home & Menu":

    st.markdown("""
    <div class="blossom-title">🌸 Blossom Restaurant 🌸</div>
    <div class="blossom-subtitle">
    Fresh Flavours • Beautiful Moments • Made with Love
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<p style='text-align:center;'>Choose your favourite dishes and add them to your cart.</p>",
        unsafe_allow_html=True
    )

    search = st.text_input(
        "🔎 Search Food",
        placeholder="Search biryani, dosa, naan..."
    )

    categories = ["All"] + sorted({
        item["category"] for item in MENU
    })

    category = st.selectbox("Food Category", categories)
    food_type = st.selectbox("Food Preference", ["All", "Veg", "Non-Veg"])

    filtered = [
        item for item in MENU
        if search.strip().lower() in item["name"].lower()
        and (category == "All" or item["category"] == category)
        and (food_type == "All" or item["type"] == food_type)
    ]

    st.write(f"**{len(filtered)} dishes found**")
    cols = st.columns(3)

    for i, item in enumerate(filtered):
        with cols[i % 3]:
            image_path = os.path.join(IMAGE_DIR, item["image"])

            if os.path.isfile(image_path):
                st.image(image_path, use_container_width=True)
            else:
                st.warning(f"Image missing: images/{item['image']}")

            st.subheader(item["name"])
            st.caption(f"{item['type']} • {item['category']}")
            st.write(item["desc"])

            # Normal-sized price
            st.markdown(
                f"<p style='font-size:20px;font-weight:600;color:#49343c;'>₹{item['price']}</p>",
                unsafe_allow_html=True
            )

            quantity = st.number_input(
                "Quantity",
                min_value=1,
                max_value=20,
                value=1,
                key=f"qty_{item['id']}"
            )

            if st.button(
                "🛒 Add to Cart",
                key=f"add_{item['id']}",
                use_container_width=True
            ):
                name = item["name"]
                st.session_state.cart[name] = (
                    st.session_state.cart.get(name, 0) + quantity
                )
                st.success(f"{name} added to cart!")

# ==================== CART AND CHECKOUT ====================

elif page == "Cart & Checkout":

    st.title("🛒 Cart & Checkout")

    if not st.session_state.cart:
        st.info("Your cart is empty. Add food from Home & Menu.")

    else:
        food_total = 0

        for name, quantity in list(st.session_state.cart.items()):
            item = next(
                (m for m in MENU if m["name"] == name), None
            )

            if item is None:
                continue

            subtotal = item["price"] * quantity
            food_total += subtotal

            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"**{name}**")
                c1.write(f"₹{item['price']} each")
                c2.write(f"Quantity: {quantity}")
                c3.write(f"Subtotal: ₹{subtotal}")

                a, b, c = st.columns(3)

                if a.button("Remove", key=f"remove_{item['id']}"):
                    del st.session_state.cart[name]
                    st.rerun()

                if b.button("−", key=f"minus_{item['id']}"):
                    if quantity > 1:
                        st.session_state.cart[name] -= 1
                    else:
                        del st.session_state.cart[name]
                    st.rerun()

                if c.button("+", key=f"plus_{item['id']}"):
                    if quantity < 20:
                        st.session_state.cart[name] += 1
                    st.rerun()

        delivery_fee = 30 if food_total > 0 else 0
        total = food_total + delivery_fee

        st.divider()
        st.write(f"Food total: ₹{food_total}")
        st.write(f"Delivery fee: ₹{delivery_fee}")
        st.subheader(f"Total: ₹{total}")

        with st.form("checkout_form"):
            st.subheader("Delivery Details")
            customer = st.text_input("Full Name")
            phone = st.text_input("10-digit Phone Number")
            address = st.text_area("Delivery Address")
            payment = st.selectbox(
                "Payment Method",
                ["Cash on Delivery", "UPI on Delivery"]
            )

            submit = st.form_submit_button(
                "Place Order",
                use_container_width=True
            )

        if submit:
            if not customer.strip():
                st.error("Please enter your name.")

            elif not phone.isdigit() or len(phone) != 10:
                st.error("Enter a valid 10-digit phone number.")

            elif not address.strip():
                st.error("Please enter your delivery address.")

            elif not st.session_state.cart:
                st.error("Your cart is empty.")

            else:
                order_id = "BL" + uuid.uuid4().hex[:8].upper()
                order_items = []

                for name, quantity in st.session_state.cart.items():
                    item = next(m for m in MENU if m["name"] == name)

                    order_items.append({
                        "name": name,
                        "price": item["price"],
                        "quantity": quantity,
                        "subtotal": item["price"] * quantity
                    })

                order = {
                    "order_id": order_id,
                    "id": order_id,
                    "customer": customer.strip(),
                    "phone": phone,
                    "address": address.strip(),
                    "payment": payment,
                    "items": order_items,
                    "food_total": food_total,
                    "delivery_fee": delivery_fee,
                    "total": total,
                    "status": "Order Placed",
                    "created_at": datetime.now().strftime(
                        "%d-%m-%Y %H:%M:%S"
                    )
                }

                st.session_state.orders.append(order)
                save_orders()
                st.session_state.last_order = order_id
                st.session_state.cart = {}

                st.success("Order placed successfully!")
                st.markdown(f"### Your Order ID: `{order_id}`")
                st.info("Save this ID to track your order.")

# ==================== TRACK ORDER ====================

elif page == "Track Order":

    st.title("📦 Track Your Order")

    order_id = st.text_input(
        "Enter Order ID",
        value=st.session_state.last_order,
        placeholder="Example: BL1234ABCD"
    )

    if st.button("Track Order", use_container_width=True):

        order = next(
            (
                saved for saved in st.session_state.orders
                if saved.get("order_id", saved.get("id", "")).lower()
                == order_id.strip().lower()
            ),
            None
        )

        if not order:
            st.error("Order not found. Check your Order ID.")

        else:
            st.success("Order found!")
            st.write(f"**Order ID:** {order['order_id']}")
            st.write(f"**Customer:** {order['customer']}")
            st.write(f"**Date:** {order['created_at']}")
            st.write(f"**Status:** {order['status']}")
            st.subheader(f"Total: ₹{order['total']}")

            st.write("**Items ordered:**")

            for item in order["items"]:
                st.write(
                    f"- {item['name']} × {item['quantity']} — ₹{item['subtotal']}"
                )

            steps = [
                "Order Placed",
                "Preparing",
                "Out for Delivery",
                "Delivered"
            ]

            if order["status"] in steps:
                current = steps.index(order["status"])

                for index, step in enumerate(steps):
                    symbol = "✅" if index <= current else "○"
                    st.write(f"{symbol} {step}")

            elif order["status"] == "Cancelled":
                st.error("This order was cancelled.")

# ==================== ADMIN DASHBOARD ====================

elif page == "Admin Dashboard":

    st.title("🔐 Admin Dashboard")

    if not st.session_state.admin_logged:

        with st.form("admin_login"):
            st.subheader("Admin Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login = st.form_submit_button("Login")

        if login:
            if username == "admin" and password == "Admin@123":
                st.session_state.admin_logged = True
                st.rerun()
            else:
                st.error("Incorrect username or password.")

    else:

        if st.button("Logout"):
            st.session_state.admin_logged = False
            st.rerun()

        orders = st.session_state.orders

        active_orders = [
            order for order in orders
            if order["status"] not in ["Delivered", "Cancelled"]
        ]

        revenue = sum(
            order["total"] for order in orders
            if order["status"] != "Cancelled"
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Orders", len(orders))
        c2.metric("Active Orders", len(active_orders))
        c3.metric("Revenue", f"₹{revenue}")

        st.subheader("Manage Orders")

        if not orders:
            st.info("No orders available yet.")

        statuses = [
            "Order Placed",
            "Preparing",
            "Out for Delivery",
            "Delivered",
            "Cancelled"
        ]

        for order in reversed(orders):

            order_id = order.get("order_id", order.get("id", "Unknown"))

            with st.expander(
                f"{order_id} | {order['customer']} | ₹{order['total']}"
            ):
                st.write(f"Phone: {order['phone']}")
                st.write(f"Address: {order['address']}")
                st.write(f"Payment: {order['payment']}")
                st.write(f"Date: {order['created_at']}")

                for item in order["items"]:
                    st.write(
                        f"- {item['name']} × {item['quantity']}"
                    )

                current_status = order.get("status", "Order Placed")

                selected_status = st.selectbox(
                    "Order Status",
                    statuses,
                    index=(
                        statuses.index(current_status)
                        if current_status in statuses else 0
                    ),
                    key=f"status_{order_id}"
                )

                if st.button(
                    "Update Status",
                    key=f"update_{order_id}"
                ):
                    for saved_order in st.session_state.orders:
                        saved_id = saved_order.get(
                            "order_id", saved_order.get("id", "")
                        )

                        if saved_id == order_id:
                            saved_order["order_id"] = order_id
                            saved_order["id"] = order_id
                            saved_order["status"] = selected_status
                            break

                    save_orders()
                    st.success("Order status updated successfully!")
                    st.rerun()

        # ==================== SALES REPORT ====================

        if orders:
            report_data = []

            for order in orders:
                report_data.append({
                    "Order ID": order.get("order_id", order.get("id", "")),
                    "Customer": order.get("customer", ""),
                    "Phone": order.get("phone", ""),
                    "Address": order.get("address", ""),
                    "Total": order.get("total", 0),
                    "Payment": order.get("payment", ""),
                    "Status": order.get("status", ""),
                    "Date": order.get("created_at", "")
                })

            report = pd.DataFrame(report_data)

            st.subheader("📊 Restaurant Sales Report")
            st.dataframe(report, use_container_width=True)

            st.download_button(
                "⬇️ Download Orders CSV",
                data=report.to_csv(index=False).encode("utf-8"),
                file_name="blossom_orders.csv",
                mime="text/csv"
            )