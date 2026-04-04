"""
DevOps Attendance Dashboard - Main Application
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import auth
import db

st.markdown("""
<style>
body {
    background-color: #ffffff;
}

.stApp {
    background-color: #ffffff;
    color: black;
}

h1, h2, h3, h4 {
    color: #2c3e50;
}

.stButton>button {
    background-color: #4CAF50;
    color: white;
    border-radius: 8px;
}

.stSidebar {
    background-color: #f5f5f5;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="DevOps Attendance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'email' not in st.session_state:
        st.session_state.email = None
    if 'page' not in st.session_state:
        st.session_state.page = 'login'

def login_page():
    """Display login page"""
    st.markdown("<h1 style='text-align: center;'>Attendance Management System</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Login to your account</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Login", use_container_width=True)

            if submit:
                if not username or not password:
                    st.error("Please fill in all fields")
                else:
                    success, user, message = auth.login_user(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user['id']
                        st.session_state.username = user['username']
                        st.session_state.email = user['email']
                        st.session_state.role = user['role']   # ✅ ADD THIS
                        st.session_state.page = 'dashboard'
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

        st.markdown("---")
        st.markdown("Don't have an account?")
        if st.button("Sign Up", use_container_width=True):
            st.session_state.page = 'signup'
            st.rerun()

def signup_page():
    """Display signup page"""
    st.markdown("# 📝 Create New Account")
    st.markdown("### Sign up to get started")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("signup_form"):
            username = st.text_input("Username", placeholder="Choose a username (3-20 characters)")
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Choose a password (min 6 characters)")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            submit = st.form_submit_button("Sign Up", use_container_width=True)

            if submit:
                if not username or not email or not password or not confirm_password:
                    st.error("Please fill in all fields")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = auth.signup_user(username, email, password)
                    if success:
                        st.success(message)
                        st.info("Please login with your credentials")
                        st.session_state.page = 'login'
                        st.rerun()
                    else:
                        st.error(message)

        st.markdown("---")
        st.markdown("Already have an account?")
        if st.button("Login", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()

def dashboard_page():
    """Display main dashboard"""
    st.markdown(f"# 📊 Welcome, {st.session_state.username}!")
    st.markdown("### Your Attendance Overview")

    stats = db.get_attendance_stats(st.session_state.user_id)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="📅 Total Days Recorded",
            value=stats['total_days'],
            delta=None
        )

    with col2:
        st.metric(
            label="✅ Present Days",
            value=stats['present_days'],
            delta=None
        )

    with col3:
        st.metric(
            label="📈 Attendance Rate",
            value=f"{stats['percentage']}%",
            delta=None
        )

    st.markdown("---")

    attendance_records = db.get_user_attendance(st.session_state.user_id)

    if attendance_records:
        st.markdown("### 📈 Attendance Trend (Last 30 Days)")

        df = pd.DataFrame(attendance_records)
        df['date'] = pd.to_datetime(df['date'])

        thirty_days_ago = datetime.now() - timedelta(days=30)
        df_recent = df[df['date'] >= thirty_days_ago].copy()

        if not df_recent.empty:
            df_recent['count'] = 1
            daily_attendance = df_recent.groupby('date')['count'].sum().reset_index()
            daily_attendance = daily_attendance.sort_values('date')

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Daily Attendance")
                st.line_chart(daily_attendance.set_index('date')['count'])

            with col2:
                st.markdown("#### Recent Activity")
                recent_5 = df.head(5)[['date', 'time', 'status']]
                st.dataframe(recent_5, use_container_width=True, hide_index=True)
        else:
            st.info("No attendance records in the last 30 days")
    else:
        st.info("No attendance records yet. Mark your first attendance!")

def mark_attendance_page():
    """Display mark attendance page"""
    st.markdown("# ✅ Mark Attendance")
    st.markdown("### Clock in for today")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        current_date = datetime.now().strftime("%B %d, %Y")
        current_time = datetime.now().strftime("%I:%M %p")

        st.markdown(f"#### 📅 Date: {current_date}")
        st.markdown(f"#### 🕐 Time: {current_time}")

        st.markdown("---")

        if st.button("✅ Mark Attendance", use_container_width=True, type="primary"):
            success, message = db.mark_attendance(st.session_state.user_id)
            if success:
                st.success(message)
                st.balloons()
            else:
                st.warning(message)

        st.markdown("---")

        today_records = db.get_user_attendance(
            st.session_state.user_id,
            start_date=datetime.now().strftime("%Y-%m-%d"),
            end_date=datetime.now().strftime("%Y-%m-%d")
        )

        if today_records:
            st.markdown("#### Today's Status: ✅ Present")
            st.markdown(f"**Marked at:** {today_records[0]['time']}")
        else:
            st.markdown("#### Today's Status: ⏳ Not Marked")

def view_attendance_page():
    """Display view attendance page"""
    st.markdown("# 📋 View Attendance Records")
    st.markdown("### Your attendance history")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30),
            max_value=datetime.now()
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            max_value=datetime.now()
        )

    attendance_records = db.get_user_attendance(
        st.session_state.user_id,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d")
    )

    if attendance_records:
        df = pd.DataFrame(attendance_records)

        col1, col2 = st.columns([3, 1])

        with col2:
            sort_order = st.selectbox("Sort by", ["Newest First", "Oldest First"])

        if sort_order == "Oldest First":
            df = df.sort_values('date', ascending=True)
        else:
            df = df.sort_values('date', ascending=False)

        display_df = df[['date', 'time', 'status']].copy()
        display_df.columns = ['Date', 'Time', 'Status']

        st.markdown(f"### Total Records: {len(display_df)}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"attendance_{start_date}_to_{end_date}.csv",
            mime="text/csv"
        )
    else:
        st.info("No attendance records found for the selected period")

def profile_page():
    """Display profile page"""
    st.markdown("# 👤 Profile")
    st.markdown("### Your account information")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### 📧 Account Details")

        user = db.get_user_by_id(st.session_state.user_id)

        info_col1, info_col2 = st.columns(2)

        with info_col1:
            st.markdown(f"**Username:** {user['username']}")
            st.markdown(f"**Email:** {user['email']}")

        with info_col2:
            created_at = datetime.strptime(user['created_at'], "%Y-%m-%d %H:%M:%S")
            st.markdown(f"**Member Since:** {created_at.strftime('%B %d, %Y')}")

        st.markdown("---")

        st.markdown("#### 🔒 Change Password")

        with st.form("change_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_new_password = st.text_input("Confirm New Password", type="password")
            submit = st.form_submit_button("Update Password")

            if submit:
                if not current_password or not new_password or not confirm_new_password:
                    st.error("Please fill in all fields")
                elif not auth.verify_password(current_password, user['password_hash']):
                    st.error("Current password is incorrect")
                elif new_password != confirm_new_password:
                    st.error("New passwords do not match")
                else:
                    is_valid, message = auth.validate_password(new_password)
                    if not is_valid:
                        st.error(message)
                    else:
                        new_hash = auth.hash_password(new_password)
                        db.update_user_password(st.session_state.user_id, new_hash)
                        st.success("Password updated successfully!")

def main():
    """Main application"""
    db.init_database()
    init_session_state()

    # 🔒 NOT LOGGED IN
    if not st.session_state.authenticated:
        if st.session_state.page == 'signup':
            signup_page()
        else:
            login_page()
        return   # 🔥 VERY IMPORTANT

    # 🔓 LOGGED IN USER

    st.sidebar.markdown(f"### 👋 Hello, {st.session_state.username}")
    st.sidebar.markdown("---")

    # ✅ ROLE-BASED NAVIGATION
    if st.session_state.role == "admin":
        pages = ["📊 Dashboard", "✅ Mark Attendance", "📋 View Attendance", "👤 Profile", "👨‍💼 Admin", "🚪 Logout"]
    else:
        pages = ["📊 Dashboard", "✅ Mark Attendance", "📋 View Attendance", "👤 Profile", "🚪 Logout"]

    page = st.sidebar.radio("Navigation", pages, label_visibility="collapsed")

    # 📊 Sidebar stats
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Quick Stats")

    stats = db.get_attendance_stats(st.session_state.user_id)
    st.sidebar.metric("Attendance Rate", f"{stats['percentage']}%")
    st.sidebar.metric("Days Present", stats['present_days'])

    # 🔀 ROUTING
    if page == "📊 Dashboard":
        dashboard_page()

    elif page == "✅ Mark Attendance":
        mark_attendance_page()

    elif page == "📋 View Attendance":
        view_attendance_page()

    elif page == "👤 Profile":
        profile_page()

    elif page == "👨‍💼 Admin":
        if st.session_state.role != "admin":
            st.warning("🚫 You are not authorized to view this page")
            st.stop()   # 🔥 VERY IMPORTANT

        admin_dashboard()   # ✅ CALL FUNCTION

    elif page == "🚪 Logout":
        auth.logout_user(st.session_state)
        st.rerun()

    def admin_dashboard():
        st.markdown("# 👨‍💼 Admin Dashboard")

    tab1, tab2 = st.tabs(["Users", "Attendance"])

    # USERS
    with tab1:
        users = db.get_all_users()
        if users:
            df = pd.DataFrame(users)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d')
            df.columns = ['ID', 'Username', 'Email', 'Role', 'Created At']
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No users found")

    # ATTENDANCE
    with tab2:
        records = db.get_all_attendance()

        if records:
            df = pd.DataFrame(records)

            df = df[['username', 'email', 'date', 'time', 'status', 'marked_by']]
            df.columns = ['Username', 'Email', 'Date', 'Time', 'Status', 'Marked By']

            user_filter = st.selectbox("Filter by user", ["All"] + list(df['Username'].unique()))

            if user_filter != "All":
                df = df[df['Username'] == user_filter]

            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False)
            st.download_button("Download CSV", csv, "attendance.csv")

        else:
            st.info("No attendance records")

    st.markdown("---")

    # ADMIN MARK ATTENDANCE
    st.subheader("Mark Attendance for Student")

    users = db.get_all_users()
    student_users = [u for u in users if u['role'] == 'student']

    if student_users:
        selected = st.selectbox("Select Student", [u['username'] for u in student_users])

        selected_user = next(u for u in student_users if u['username'] == selected)

        if st.button("Mark Attendance (Admin)"):
            success, msg = db.mark_attendance(selected_user['id'], marked_by="admin")
            if success:
                st.success(msg)
            else:
                st.warning(msg)

if __name__ == "__main__":
    main()
