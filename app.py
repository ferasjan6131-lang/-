import streamlit as st
import pandas as pd
from datetime import datetime

# إعدادات الصفحة لتناسب الجوال والكمبيوتر
st.set_page_config(page_title="نظام مصاريف المطعم المشترك", layout="centered", initial_sidebar_state="collapsed")

# 1. نظام حماية ودخول بسيط للموقع
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>🔐 تسجيل الدخول للموقع</h2>", unsafe_allow_html=True)
    username = st.text_input("اسم المستخدم (أنت أو أخوك)")
    password = st.text_input("كلمة المرور", type="password")
    login_btn = st.button("دخول", use_container_width=True)
    
    # يمكنك تغيير كلمة المرور هنا كما تحب
    if login_btn:
        if password == "0532660073" and username in ["عبدالمجيد", "فراس", "فارس"]: 
            st.session_state.authenticated = True
            st.session_state.user = username
            st.rerun()
        else:
            st.error("اسم المستخدم أو كلمة المرور غير صحيحة!")
    st.stop()

# 2. تهيئة قاعدة البيانات المحلية لحفظ الفواتير (في الجلسة الحالية)
if 'restaurant_db' not in st.session_state:
    st.session_state.restaurant_db = pd.DataFrame(columns=['التاريخ والوقت', 'المسؤول', 'الغرض', 'المبلغ (ريال)', 'النوع'])

# 3. واجهة الموقع بعد الدخول
st.markdown(f"<h3 style='text-align: center;'>🏪 نظام مصاريف المطعم المشترك</h3>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: green;'>مرحباً بك يا <b>{st.session_state.user}</b> | الآن يمكنك تسجيل أي مصروف فوراً</p>", unsafe_allow_html=True)

# استمارة إدخال المصاريف السريعة
with st.form("expense_form", clear_on_submit=True):
    st.markdown("#### 🛒 تسجيل غرض جديد")
    item_name = st.text_input("ماذا اشتريت الآن؟", placeholder="مثال: كيس رز، طماطم، فاتورة كهرباء...")
    amount = st.number_input("المبلغ المدفوع (ريال سعودي)", min_value=0.0, step=1.0, value=0.0)
    category = st.selectbox("تصنيف المصروف", ["خضار وفواكه", "لحوم ودواجن", "مواد جافة", "فواتير وتشغيل", "أدوات سفري", "أخرى"])
    
    submit_btn = st.form_submit_button("🚀 حفظ المصروف الآن", use_container_width=True)
    
    if submit_btn:
        if item_name and amount > 0:
            now_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            # إضافة البيانات وتحديد من قام بالإدخال 
            new_data = pd.DataFrame([[now_str, st.session_state.user, item_name, amount, category]], columns=st.session_state.restaurant_db.columns)
            st.session_state.restaurant_db = pd.concat([new_data, st.session_state.restaurant_db], ignore_index=True)
            st.success(f"تم حفظ '{item_name}' بنجاح بواسطة {st.session_state.user}!")
        else:
            st.error("تأكد من كتابة اسم الغرض والمبلغ بشكل صحيح.")

st.markdown("---")

# 4. لوحة تحليلات آخر الليل والتقرير الإجمالي
st.markdown("### 📊 كشف حساب ومصاريف اليوم")

if not st.session_state.restaurant_db.empty:
    # حساب الإجمالي
    total_spent = st.session_state.restaurant_db['المبلغ (ريال)'].sum()
    st.metric(label="💰 إجمالي المشتريات والمصاريف حتى الآن", value=f"{total_spent:,.2f} ريال")
    
    # عرض الجدول المشترك
    st.markdown("**📄 قائمة المشتريات المسجلة بالتفصيل:**")
    st.dataframe(st.session_state.restaurant_db, use_container_width=True)
    
    # ميزة تحميل التقرير إكسل في آخر الليل
    csv = st.session_state.restaurant_db.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 تحميل كشف الحساب بصيغة Excel/CSV",
        data=csv,
        file_name=f"مصاريف_المطعم_{datetime.now().strftime('%Y-%m-%d')}.csv",
        mime='text/csv',
        use_container_width=True
    )
else:
    st.info("لا توجد مصاريف مسجلة لليوم حتى الآن. بانتظار إدخالك أو إدخال أخيك!")

# زر خروج للأمان
if st.button("📴 تسجيل الخروج"):
    st.session_state.authenticated = False
    st.rerun()
