import streamlit as st
import pandas as pd
import os
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="نظام المبيعات والمصاريف", layout="centered", initial_sidebar_state="collapsed")

# اسم الملف الذي ستحفظ فيه البيانات تلقائياً
DATA_FILE = "data.csv"

# دالة لتحميل البيانات من الملف
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=['التاريخ والوقت', 'المسؤول', 'النوع', 'الوصف/الطلب', 'المبلغ (ريال)', 'طريقة الدفع', 'التصنيف'])

# دالة لحفظ البيانات فوراً في الملف
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# 1. تسجيل الدخول
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>🔐 تسجيل الدخول</h2>", unsafe_allow_html=True)
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("دخول", use_container_width=True):
        if password == "12345" and username.strip() != "فراس":
            st.session_state.authenticated = True
            st.session_state.user = username
            st.rerun()
        else:
            st.error("اكتب اسمك وكلمة المرور الصحيحة (12345)")
    st.stop()

# تحميل البيانات الحالية
df_data = load_data()

st.markdown(f"<h3 style='text-align: center;'>🏪 نظام مبيعات ومصاريف المطعم</h3>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: green;'>مرحباً <b>{st.session_state.user}</b> | الحفظ تلقائي ودائم 💾</p>", unsafe_allow_html=True)

# 2. إدخال بيانات جديدة
entry_type = st.radio("اختر نوع العملية:", ["💵 بيع (إيراد)", "🛒 مصروف (مشتريات/فواتير)"], horizontal=True)

with st.form("entry_form", clear_on_submit=True):
    if "بيع" in entry_type:
        st.markdown("#### 💵 تسجيل عملية بيع")
        item_desc = st.text_input("تفاصيل الطلب / الوجبة", placeholder="مثال: وجبة شواية + بيبسي")
        amount = st.number_input("المبلغ (ريال)", min_value=0.0, step=1.0, value=0.0)
        pay_method = st.selectbox("طريقة الدفع", ["شبكة / مدى", "كاش (نقدي)", "تطبيق توصيل", "آجل"])
        category = st.selectbox("نوع الطلب", ["محلي", "سفري", "توصيل"])
        record_type = "بيع"
    else:
        st.markdown("#### 🛒 تسجيل مصروف جديد")
        item_desc = st.text_input("ماذا اشتريت؟", placeholder="مثال: خضار، فاتورة كهرباء")
        amount = st.number_input("المبلغ المدفوع (ريال)", min_value=0.0, step=1.0, value=0.0)
        pay_method = st.selectbox("طريقة الدفع", ["كاش (نقدي)", "شبكة / مدى", "آجل"])
        category = st.selectbox("تصنيف المصروف", ["خضار وفواكه", "لحوم ودواجن", "مواد جافة", "فواتير وتشغيل", "أخرى"])
        record_type = "مصروف"

    submit_btn = st.form_submit_button("🚀 حفظ العملية تلقائياً", use_container_width=True)

    if submit_btn:
        if item_desc and amount > 0:
            now_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            new_row = pd.DataFrame([[now_str, st.session_state.user, record_type, item_desc, amount, pay_method, category]], 
                                   columns=['التاريخ والوقت', 'المسؤول', 'النوع', 'الوصف/الطلب', 'المبلغ (ريال)', 'طريقة الدفع', 'التصنيف'])
            
            updated_df = pd.concat([df_data, new_row], ignore_index=True)
            save_data(updated_df) # حفظ تلقائي في الملف
            st.success(f"تم حفظ {record_type} بمبلغ {amount:,.2f} ريال بنجاح ولن يختفي!")
            st.rerun()
        else:
            st.error("يرجى إدخال تفاصيل الطلب والمبلغ الصحيح.")

st.markdown("---")

# 3. عرض المبيعات والمصاريف والإجمالي
st.markdown("### 📊 السجل والميزانية الحالية")

df_data = load_data()

if not df_data.empty:
    sales_total = df_data[df_data['النوع'] == 'بيع']['المبلغ (ريال)'].sum()
    expenses_total = df_data[df_data['النوع'] == 'مصروف']['المبلغ (ريال)'].sum()
    net_profit = sales_total - expenses_total

    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المبيعات 💵", f"{sales_total:,.2f} ريال")
    col2.metric("إجمالي المصاريف 🛒", f"{expenses_total:,.2f} ريال")
    col3.metric("الصافي 💰", f"{net_profit:,.2f} ريال")

    st.markdown("**📄 السجل الكامل المحفوظ:**")
    st.dataframe(df_data, use_container_width=True)
else:
    st.info("لا توجد عمليات مسجلة حتى الآن.")

if st.button("📴 تسجيل الخروج"):
    st.session_state.authenticated = False
    st.rerun()
