import streamlit as st
import team5
import time
import sys
import os
# هذا الكود يجعل الصفحة تبحث عن الملفات في المجلد الخارجي أيضاً
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '')))
try:
    st.set_page_config(page_title="Payment", layout="wide")
except:
    pass

st.title("💳 Secure Checkout")

# زر العودة للصفحة الرئيسية
if st.button("⬅️ Back to Home"):
    st.switch_page("Homepage.py")

st.write("---")

if 'payment_success' not in st.session_state:
    st.session_state['payment_success'] = False

# التأكد من وجود مستخدم (اختياري لكن يفضل)
user_id = st.session_state.get('user_id')

payment_method = st.radio("Choose Payment Method:", ("Visa", "Cash on Delivery"))
st.write("---")

if payment_method == "Visa":
    st.subheader("Visa Details")
    col1, col2 = st.columns(2)
    with col1:
        visa_number = st.text_input("Card Number (16 digits)", max_chars=16)
        expire_date = st.text_input("Expiry Date (MM/YY)")
    with col2:
        cvv_number = st.text_input("CVV (3 digits)", max_chars=3, type="password")
        
    if st.button("Submit Payment", type="primary") or st.session_state['payment_success']:
        errors = False
        if not st.session_state['payment_success']:
            if len(visa_number) != 16 or not visa_number.isdigit():
                st.error("Warning: Visa number must be exactly 16 digits.")
                errors = True
            if len(cvv_number) != 3 or not cvv_number.isdigit():
                st.error("Warning: CVV must be exactly 3 digits.")
                errors = True
        
        if not errors:
            st.session_state['payment_success'] = True
            st.balloons()
            st.success("Payment Successful! Your order has been placed.")
            
            # هنا يمكنك إضافة كود لحفظ الطلب في الداتا بيز وتفريغ السلة
            # team5.save_payment(...) 
            # team5.clear_cart(user_id) ...

            st.write("---")
            st.write("### Rate your experience")
            sentiment = st.feedback("stars")
            if sentiment is not None:
                st.write("Thank you for rating!")
                time.sleep(2)
                st.switch_page("Homepage.py")
            # زر للعودة بعد الدفع
            #if st.button("🏠 Return to Shop"):
                

elif payment_method == "Cash on Delivery":
    st.info("You will pay when the order arrives.")
    if st.button("Confirm Order", type="primary"):
        st.session_state['payment_success'] = True
        st.snow()
        st.success("Order Confirmed!")
        time.sleep(2)
        st.switch_page("Homepage.py")