import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# إعدادات الصفحة
st.set_page_config(page_title="نظام مبيعات المطعم", layout="centered", initial_sidebar_state="collapsed")

# 1. نظام حماية ودخول بسيط للموقع (كلمة المرور فقط: 12345)
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>🔐 تسجيل الدخول - نظام المبيعات</h2>", unsafe_allow_html=True)
    username = st.text_input("اسمك (مثال: أحمد / خالد)")
    password = st.text_input("كلمة المرور", type="password")
    login_btn = st.button("دخول", use_container_width=True)
    
    if login_btn:
        if password == "12345" and username.strip() != "": 
            st.session_state.authenticated = True
            st.session_state.user = username
            st.rerun()
        else:
            st.error("تأكد من كتابة اسمك وكلمة المرور الصحيحة (12345)")
    st.stop()

# 2. الربط بجدول جودل شيت للحفظ الدائم
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(ttl=0)
        return df
    except Exception:
        return pd.DataFrame(columns=['التاريخ والوقت', 'الكاشير/المسؤول', 'الطلب/المنتج', 'المبلغ (ريال)', 'طريقة الدفع', 'نوع الطلب'])

sales_db = load_data()

# 3. واجهة الموقع
st.markdown(f"<h3 style='text-align: center;'>🍔 نظام مبيعات المطعم</h3>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: green;'>مرحباً بك يا <b>{st.session_state.user}</b> | البيانات محفوظة بشكل دائم 💾</p>", unsafe_allow_html=True)

# استمارة إدخال المبيعات
with st.form("sales_form", clear_on_submit=True):
    st.markdown("#### 💵 تسجيل عملية بيع جديدة")
    
    order_details = st.text_input("تفاصيل الطلب / الوجبة", placeholder="مثال: وجبة شواية + بيبسي")
    amount = st.number_input("المبلغ الإجمالي (ريال سعودي)", min_value=0.0, step=1.0, value=0.0)
    
    col1, col2 = st.columns(2)
    with col1:
        payment_method = st.selectbox("طريقة الدفع", ["شبكة / مدى", "كاش (نقدي)", "تطبيق توصيل", "آجل"])
    with col2:
        order_type = st.selectbox("نوع الطلب", ["محلي", "سفري", "توصيل"])
    
    submit_btn = st.form_submit_button("🚀 حفظ العملية دائماً", use_container_width=True)
    
    if submit_btn:
        if order_details and amount > 0:
            now_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            new_sale = pd.DataFrame([[now_str, st.session_state.user, order_details, amount, payment_method, order_type]], 
                                    columns=['التاريخ والوقت', 'الكاشير/المسؤول', 'الطلب/المنتج', 'المبلغ (ريال)', 'طريقة الدفع', 'نوع الطلب'])
            
            updated_df = pd.concat([sales_db, new_sale], ignore_index=True)
            conn.update(data=updated_df)
            st.success(f"تم حفظ عملية البيع بمبلغ {amount:,.2f} ريال في قاعدة البيانات!")
            st.rerun()
        else:
            st.error("تأكد من كتابة تفاصيل الطلب والمبلغ بشكل صحيح.")

st.markdown("---")

# 4. عرض البيانات المحفوظة
st.markdown("### 📊 المبيعات المحفوظة")

sales_db = load_data()

if not sales_db.empty:
    total_sales = sales_db['المبلغ (ريال)'].sum()
    st.metric(label="💰 إجمالي المبيعات الإجمالي", value=f"{total_sales:,.2f} ريال")
    
    st.markdown("**📄 السجل الكامل للمبيعات:**")
    st.dataframe(sales_db, use_container_width=True)
else:
    st.info("لا توجد عمليات بيع مسجلة حتى الآن.")

if st.button("📴 تسجيل الخروج"):
    st.session_state.authenticated = False
    st.rerun()
