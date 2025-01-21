import streamlit as st
import pyodbc

# SQL Server connection setup
connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost,1433;"  # Update with your server and port
    "DATABASE=HardwareStore;"
    "UID=your_username;"  # Replace with your SQL Server username
    "PWD=your_password;"  # Replace with your SQL Server password
)

def get_connection():
    return pyodbc.connect(connection_string)

def get_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Products")
    products = [row[0] for row in cursor.fetchall()]
    conn.close()
    return products

def get_product_details(product_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT price, stock, description FROM Products WHERE name = ?", product_name)
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"price": result[0], "stock": result[1], "description": result[2]}
    return None

def get_order_status(order_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, delivery_date FROM Orders WHERE order_number = ?", order_number)
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"status": result[0], "delivery_date": result[1]}
    return None

# Streamlit App
st.title("Hardware Store Chatbot")
st.write("Welcome! Ask me about products, orders, or shipping.")

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Input field
with st.form(key="chat_form"):
    user_input = st.text_input("You:", "")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate response
    user_input_lower = user_input.lower()
    response = "I'm sorry, I didn't understand that. You can ask about products, orders, or shipping!"

    if "product" in user_input_lower:
        products = get_products()
        response = f"We offer the following products: {', '.join(products)}. What would you like to know?"
    elif any(product in user_input_lower for product in ["hammer", "screwdriver", "drill"]):
        product_name = [p for p in ["hammer", "screwdriver", "drill"] if p in user_input_lower][0]
        details = get_product_details(product_name.capitalize())
        if details:
            response = (
                f"{product_name.capitalize()} - Price: PHP {details['price']}, "
                f"Stock: {details['stock']} units. Description: {details['description']}."
            )
        else:
            response = f"Sorry, I couldn't find details about {product_name}."
    elif "order" in user_input_lower or "status" in user_input_lower:
        order_id = "".join(filter(str.isdigit, user_input))
        order = get_order_status(order_id)
        if order:
            response = (
                f"Order #{order_id} is currently '{order['status']}'. "
                f"Expected delivery: {order['delivery_date']}" if order["delivery_date"] else "Delivery date not yet available."
            )
        else:
            response = "I couldn't find any details for that order number."
    elif "shipping" in user_input_lower:
        response = "Shipping typically takes 3-5 business days. Would you like to know more?"

    # Add bot response to chat
    st.session_state.messages.append({"role": "bot", "content": response})

# Display messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.write(f"You: {message['content']}")
    elif message["role"] == "bot":
        st.write(f"Bot: {message['content']}")
