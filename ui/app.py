import streamlit as st
import urllib.request
import urllib.parse
import json

API_URL = "http://localhost:8000"

def fetch_json(endpoint):
    try:
        with urllib.request.urlopen(f"{API_URL}{endpoint}") as response:
            return json.loads(response.read().decode())
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def post_json(endpoint, data):
    req = urllib.request.Request(f"{API_URL}{endpoint}", data=json.dumps(data).encode(), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode()), None
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode())
            return None, err.get('detail', str(e))
        except:
            return None, str(e)
    except Exception as e:
        return None, str(e)

# Initialize Session State
if 'cart' not in st.session_state:
    st.session_state.cart = {}
if 'page' not in st.session_state:
    st.session_state.page = "Catalog"
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None

# Sidebar
st.sidebar.title("ADP Shop")
users_data = fetch_json("/users") or []
if users_data:
    user_options = [u["id"] for u in users_data]
    user_names = {u["id"]: u["name"] for u in users_data}
    user_id = st.sidebar.selectbox("Select User", options=user_options, format_func=lambda x: user_names.get(x, f"User {x}"))
else:
    user_id = st.sidebar.selectbox("Select User", options=list(range(1, 21)), format_func=lambda x: f"User {x}")
st.session_state.user_id = user_id

pages = ["Catalog", "Product", "Cart", "Orders", "Databases"]
def set_page(page_name):
    st.session_state.page = page_name

for p in pages:
    if st.sidebar.button(p, use_container_width=True):
        set_page(p)

st.sidebar.write(f"Items in cart: {sum(st.session_state.cart.values())}")

page = st.session_state.page

if page == "Catalog":
    st.title("Catalog")
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Category", ["All", "laptops", "shoes", "books", "phones"])
    with col2:
        search_q = st.text_input("Search Name")
        
    query = []
    if category != "All":
        query.append(f"category={urllib.parse.quote(category)}")
    if search_q:
        query.append(f"q={urllib.parse.quote(search_q)}")
        
    qs = "&".join(query)
    endpoint = f"/products?{qs}" if qs else "/products"
    products = fetch_json(endpoint)
    
    if products:
        for p in products:
            with st.container():
                st.subheader(p['name'])
                st.write(f"Category: {p['category']} | Price: ${p['price']}")
                if st.button(f"View Details", key=f"view_{p['product_id']}"):
                    st.session_state.selected_product = p['product_id']
                    set_page("Product")
                    st.rerun()
                st.divider()

elif page == "Product":
    if not st.session_state.selected_product:
        st.write("No product selected. Go to Catalog.")
    else:
        pid = st.session_state.selected_product
        if st.button("Back to Catalog"):
            set_page("Catalog")
            st.rerun()
            
        prod = fetch_json(f"/products/{pid}")
        if prod:
            st.title(prod['name'])
            st.write(f"**Price**: ${prod['price']}")
            st.write(f"**Category**: {prod['category']}")
            st.write(f"**Stock**: {prod.get('stock', 0)}")
            st.write(f"**Description**: {prod['description']}")
            
            st.subheader("Attributes")
            for k, v in prod.get('attributes', {}).items():
                st.write(f"- {k}: {v}")
                
            qty = st.number_input("Quantity", min_value=1, max_value=max(1, prod.get('stock', 1)), value=1)
            if st.button("Add to Cart"):
                if prod.get('stock', 0) >= qty:
                    st.session_state.cart[pid] = st.session_state.cart.get(pid, 0) + qty
                    st.success("Added to cart!")
                else:
                    st.error("Not enough stock!")
            
            st.subheader("Reviews")
            for r in prod.get('reviews', []):
                st.write(f"**{r['user']}** ({r['rating']}/5): {r['text']}")
                
            st.subheader("Similar Products")
            similar = fetch_json(f"/products/{pid}/similar")
            if similar:
                for s in similar:
                    st.write(f"- {s['name']} (${s['price']})")
                    if st.button(f"View {s['product_id']}", key=f"sim_{s['product_id']}"):
                        st.session_state.selected_product = s['product_id']
                        st.rerun()
            else:
                st.write("No similar products found.")

elif page == "Cart":
    st.title("Cart & Checkout")
    if not st.session_state.cart:
        st.write("Your cart is empty.")
    else:
        total = 0.0
        items_payload = []
        
        for pid, qty in st.session_state.cart.items():
            prod = fetch_json(f"/products/{pid}")
            if prod:
                st.write(f"**{prod['name']}** x {qty} = ${prod['price'] * qty}")
                total += prod['price'] * qty
                items_payload.append({"product_id": pid, "qty": qty})
                
        st.write(f"**Total**: ${total:.2f}")
        
        if st.button("Checkout"):
            payload = {
                "user_id": st.session_state.user_id,
                "items": items_payload
            }
            res, err = post_json("/orders", payload)
            if err:
                st.error(f"Checkout failed: {err}")
            else:
                st.success(f"Order {res['order_id']} placed successfully!")
                st.session_state.cart = {}
                st.rerun()
                
        if st.button("Clear Cart"):
            st.session_state.cart = {}
            st.rerun()

elif page == "Orders":
    st.title("Order History")
    orders = fetch_json(f"/orders?user_id={st.session_state.user_id}")
    if orders:
        for o in orders:
            with st.expander(f"Order #{o['id']} - ${o['total']} - {o['status']} ({o['created_at']})"):
                items = fetch_json(f"/orders/{o['id']}/items")
                if items:
                    for i in items:
                        st.write(f"- {i['product_name']} (Qty: {i['qty']}, Price: ${i['price']})")
    else:
        st.write("No orders found.")

elif page == "Databases":
    st.title("Recent DB Requests")
    debug_info = fetch_json("/debug/requests")
    if debug_info and 'requests' in debug_info:
        st.table(debug_info['requests'])
    else:
        st.write("No requests logged yet.")
