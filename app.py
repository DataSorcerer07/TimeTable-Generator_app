import mysql.connector
import random
import pandas as pd
import streamlit as st
from io import BytesIO

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ultimus",
    database="class_scheduler"
)

def get_batch(year, dept, section):
    cur = db.cursor(dictionary=True, buffered=True)
    cur.execute("""
        SELECT * FROM Batch WHERE year=%s AND dept=%s AND section=%s
    """, (year, dept, section))
    result = cur.fetchone()
    cur.close()
    return result

def get_subjects_for_batch(batch_id):
    cur = db.cursor(dictionary=True, buffered=True)
    cur.execute("""
        SELECT s.subject_id, 
               s.subject_name, 
               f.name AS teacher_name
        FROM Batch_Subject bs
        JOIN Subject s ON bs.subject_id = s.subject_id
        LEFT JOIN Teacher f ON s.teacher_id = f.teacher_id
        WHERE bs.batch_id=%s
    """, (batch_id,))
    result = cur.fetchall()
    cur.close()
    return result

def get_teacher(username, password):
    cur = db.cursor(dictionary=True, buffered=True)
    cur.execute("""
        SELECT * FROM Teacher WHERE teacher_id=%s AND dept=%s
    """, (username, password))
    result = cur.fetchone()
    cur.close()
    return result

def get_teacher_schedule(teacher_id):
    cur = db.cursor(dictionary=True, buffered=True)
    cur.execute("""
        SELECT s.subject_name, b.year, b.dept, b.section
        FROM Subject s
        JOIN Batch_Subject bs ON s.subject_id = bs.subject_id
        JOIN Batch b ON b.batch_id = bs.batch_id
        WHERE s.teacher_id=%s
    """, (teacher_id,))
    result = cur.fetchall()
    cur.close()
    return result

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
PERIODS = ["Period 1", "Period 2", "Period 3", "Period 4", "Period 5"]

def parse_availability(avail_str):
    days, hours = avail_str.split(" ")
    start_day, end_day = days.split("-")
    start_time, end_time = hours.split("-")
    day_map = {
        "Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday",
        "Thu": "Thursday", "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday",
        "Monday": "Monday", "Tuesday": "Tuesday", "Wednesday": "Wednesday",
        "Thursday": "Thursday", "Friday": "Friday"
    }

    start_day = day_map.get(start_day, start_day)
    end_day = day_map.get(end_day, end_day)

    if start_day not in WEEKDAYS or end_day not in WEEKDAYS:
        return {}
    weekdays = WEEKDAYS[WEEKDAYS.index(start_day):WEEKDAYS.index(end_day) + 1]

    start_hour = int(start_time.split(":")[0])
    end_hour = int(end_time.split(":")[0])

    available_periods = {}
    for day in weekdays:
        available_periods[day] = []
        for i, period in enumerate(PERIODS, start=1):
            period_hour = 8 + i
            if start_hour <= period_hour < end_hour:
                available_periods[day].append(period)
    return available_periods

def generate_timetable(batch):
    subjects = get_subjects_for_batch(batch["batch_id"])
    if not subjects:
        return None

    subject_pairs = [
        f"{subj['subject_name']} ({subj['teacher_name'] if subj['teacher_name'] else 'TBD'})"
        for subj in subjects
    ]

    full_list = []
    while len(full_list) < len(WEEKDAYS) * len(PERIODS):
        full_list.extend(subject_pairs)
    full_list = full_list[:25]
    random.shuffle(full_list)

    timetable = {day: {} for day in WEEKDAYS}
    i = 0
    for day in WEEKDAYS:
        for period in PERIODS:
            timetable[day][period] = full_list[i]
            i += 1
    return timetable

def home_page():
    render_title("Home")
    # Page background and main title
    st.markdown(
    """
    <style>
    .stApp {
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
        animation: bgChange 200s infinite; /* 10 images × 10s each */
        transition: background-image 10s ease-in-out;
    }
    @keyframes bgChange {
        0%   { background-image: url("https://oleg-schapov-studio.myshopify.com/cdn/shop/files/DJI_0482.jpg?v=1698250754&width=2400"); }
        10%  { background-image: url("https://i0.wp.com/heights-photos.s3.amazonaws.com/wp-content/uploads/2024/01/25234224/Alina1-2.jpg?fit=1528%2C838&ssl=1"); }
        20%  { background-image: url("https://oleg-schapov-studio.myshopify.com/cdn/shop/files/DJI_0482.jpg?v=1698250754&width=800"); }
        30% { background-image: url("https://collegevine.imgix.net/a67a91d0-421a-46a4-8b2d-97633690d720.jpg?fit=crop&crop=edges&auto=format"); }
        40%  { background-image: url("https://img.lovepik.com/photo/20211124/small/lovepik-university-of-cambridge-in-the-setting-sun-picture_500950359.jpg"); }
        50%  { background-image: url("https://static.vecteezy.com/system/resources/thumbnails/017/101/825/small_2x/king-s-college-campus-at-cambridge-england-photo.jpg"); }
        60%  { background-image: url("https://c4.wallpaperflare.com/wallpaper/399/576/836/academic-baltimore-building-campus-wallpaper-preview.jpg"); }
        70%  { background-image: url("https://w0.peakpx.com/wallpaper/100/792/HD-wallpaper-dome-building-at-caltech-building-university-campus-trees-sky-college.jpg"); }
        80%  { background-image: url("https://caltechsites-prod.s3.amazonaws.com/canvas/images/IMG_9899.2e16d0ba.fill-790x300-c100.jpg"); }
        90%  { background-image: url("https://plus.unsplash.com/premium_photo-1680807869624-07b389d623e8?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8Y2FtcHVzfGVufDB8fDB8fHww"); }
        100% { background-image: url("https://mitimphal.in/wp-content/uploads/2025/08/best-engineering-college-in-india.png"); }
    }
    .main-title {
        color: #000000; 
        font-size: 48px; 
        font-weight: bold; 
        text-align: center; 
        font-family: "Copperplate Gothic Bold", "Copperplate", "Copperplate Gothic", serif;
    }
    .info-box {
        background-color: #00CED1;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 3px 3px 15px rgba(255, 255, 255, 0.85);
        text-align: center;
        width: 200px;
    }
    .info-title {
        font-size: 20px;
        font-weight: bold;
        color: #000000;
    }
    .info-value {
        font-size: 28px;
        font-weight: bold;
        color: #E6E6FA;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True
)


    # College name
    st.markdown("<br>", unsafe_allow_html=True)

    # Info boxes in a row
    st.markdown(
        """
        <div style='display:flex; justify-content:center; gap:30px;'>
            <div class='info-box'>
                <div class='info-title'>No of Students</div>
                <div class='info-value'>1200</div>
            </div>
            <div class='info-box'>
                <div class='info-title'>No of Teachers</div>
                <div class='info-value'>120</div>
            </div>
            <div class='info-box'>
                <div class='info-title'>Classes scheduled</div>
                <div class='info-value'>78</div>
            </div>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # Optional: add inspiring subtitle
    st.markdown(
    '''<h3 style='text-align:center; color:#FFFFFF;font-family: "Copperplate Gothic Bold", "Copperplate", "Copperplate Gothic", serif; font-weight:bold;'>Plan your classes efficiently and inspire success!</h3>''',
    unsafe_allow_html=True
)

    st.markdown(
    """
    <style>
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-20px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideUp {
      from { opacity: 0; transform: translateY(30px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
      0% { transform: scale(1); }
      50% { transform: scale(1.05); }
      100% { transform: scale(1); }
    }

    .main-title {
      animation: fadeIn 1.5s ease-out;
    }
    .info-box {
      animation: slideUp 1s ease-out;
    }
    .info-value {
      animation: pulse 2s infinite;
    }
    @keyframes fadeSlide {
      from { opacity: 0; transform: translateY(40px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .main-title {
      animation: fadeSlide 1.2s ease-out;
    }
    .info-box {
      animation: fadeSlide 1.5s ease-out;
    }

    }
    .button:hover {
      transform: scale(1.05);
      background-color: #4B0082;
      transition: all 0.3s ease-in-out;
    }
    @keyframes float {
      0% { transform: translateY(0); }
      50% { transform: translateY(-10px); }
      100% { transform: translateY(0); }
    }

    .hero-icon {
      animation: float 3s ease-in-out infinite;
    }
    </style>
    """, unsafe_allow_html=True
)



page = st.sidebar.radio(
    "Navigate to:", 
    ["Home", "Student", "Teacher", "Admin"], 
    index=0,  # Home selected by default
    key="role_select"
)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
def admin_panel():
    st.subheader(f"⚙️ Admin Panel - Welcome {st.session_state.username}")

    table = st.selectbox("Select Table to Manage", 
                         ["Batch", "Subject", "Teacher", "Batch_Subject",
                          "classroom", "student", "Teacher_subject", "timeslot"], 
                         key="admin_table")

    operation = st.selectbox("Select Operation", 
                             ["View", "Insert", "Update", "Delete"], 
                             key="admin_operation")

    cur = db.cursor(dictionary=True, buffered=True)
    cur.execute(f"SELECT * FROM {table}")
    rows = cur.fetchall()
    cur.close()

    if operation == "View":
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode()
            st.download_button("📥 Download CSV", data=csv, 
                               file_name=f"{table}.csv", mime="text/csv")

    elif operation == "Insert":
        if rows:
            st.markdown("### ➕ Insert Record")
            new_values = {}
            for col in rows[0].keys():
                new_values[col] = st.text_input(f"Value for {col}", key=f"insert_{col}")
            if st.button("Insert Record", key="insert_btn"):
                cur = db.cursor()
                columns = ", ".join(new_values.keys())
                placeholders = ", ".join(["%s"] * len(new_values))
                query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                cur.execute(query, tuple(new_values.values()))
                db.commit()
                cur.close()
                st.success("✅ Record inserted!")
                st.rerun()

    elif operation == "Delete":
        if rows:
            st.markdown("### 🗑️ Delete Record")
            delete_id = st.text_input("Enter ID to delete", key="delete")
            if st.button("Delete Record", key="delete_btn"):
                cur = db.cursor()
                id_col = list(rows[0].keys())[0]
                cur.execute(f"DELETE FROM {table} WHERE {id_col}=%s", (delete_id,))
                db.commit()
                cur.close()
                st.success("✅ Record deleted!")
                st.rerun()

    elif operation == "Update":
        if rows:
            st.markdown("### ✏️ Update Record")
            update_id = st.text_input("Enter ID to update", key="update")
            update_col = st.text_input("Enter column to update", key="update_col")
            update_val = st.text_input("Enter new value", key="update_val")
            if st.button("Update Record", key="update_btn"):
                cur = db.cursor()
                id_col = list(rows[0].keys())[0]
                query = f"UPDATE {table} SET {update_col}=%s WHERE {id_col}=%s"
                cur.execute(query, (update_val, update_id))
                db.commit()
                cur.close()
                st.success("✅ Record updated!")
                st.rerun()

    # Logout Button
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()


def admin_login():
    render_title("Admin")
    st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://img.freepik.com/free-photo/flat-lay-workstation-with-copy-space-laptop_23-2148430879.jpg?semt=ais_incoming&w=740&q=80");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }
    </style>
    """, unsafe_allow_html=True
    )
    st.subheader("🔐 Admin Login")
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.button("Login as Admin")
    
    if login_button:
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("✅ Login successful")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")


def generate_teacher_timetable(teacher_id):
    cur = db.cursor(dictionary=True, buffered=True)
    cur.execute("SELECT * FROM Teacher WHERE teacher_id=%s", (teacher_id,))
    teacher = cur.fetchone()
    cur.close()

    if not teacher:
        return None

    schedule = get_teacher_schedule(teacher_id)
    if not schedule:
        return None

    availability = parse_availability(teacher["availability"])

    subject_pairs = [
        f"{s['subject_name']} - {s['dept']} Year {s['year']} Sec {s['section']}"
        for s in schedule
    ]

    timetable = {day: {p: "Not Available" for p in PERIODS} for day in WEEKDAYS}
    i = 0
    for day in WEEKDAYS:
        if day not in availability:
            continue
        for period in availability[day]:
            if i < len(subject_pairs):
                timetable[day][period] = subject_pairs[i]
                i += 1
            else:
                timetable[day][period] = "Free"
    return timetable
def render_title(page_name):
    titles = {
        "Home": "Welcome to ABC College Timetable System",
        "Student": "Student Dashboard",
        "Teacher": "Teacher Dashboard",
        "Admin": "Admin Dashboard"
    }
    st.markdown(f"<div class='main-title'>{titles.get(page_name, 'ABC College')}</div>", unsafe_allow_html=True)

def color_subjects(val):
    colors = {
        "Maths": "#FFD580", "Physics": "#FF9999", "Chemistry": "#99CCFF",
        "Database": "#B3FFB3", "Operating Systems": "#E6CCFF", "AI": "#FFCC99",
        "Machine Learning": "#CCE5FF", "Networks": "#FFB3E6", "Cloud": "#B3E0FF"
    }
    for key in colors:
        if key.lower() in str(val).lower():
            return f"background-color: {colors[key]}; color: black; font-weight: bold;"
    return ""
def download_timetable(df, filename="timetable.xlsx"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=True, sheet_name="Timetable")
    return output.getvalue()
st.set_page_config(page_title="Class Timetable Generator", layout="wide")

if page=="Home":
    home_page()
elif page == "Student":
    render_title("Student")
    st.markdown(
    """
    <style>
    .main-title {
      font-size: 64px;
      font-weight: 900;
      color: #000000;
      text-align: center;
      font-family: "Copperplate Gothic Bold", "Copperplate", "Copperplate Gothic", serif;
      width: 100%;
      padding: 20px 0;
      text-shadow: 2px 2px 6px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True
)
    st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1541339907198-e08756dedf3f?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8dW5pdmVyc2l0eSUyMHN0dWRlbnR8ZW58MHx8MHx8fDA%3D");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }
    </style>
    """, unsafe_allow_html=True
)
    st.markdown(
    """
    <style>
    label {
    color: #000000 !important;
    font-weight: bold;
    font-size: 24px;
    text-shadow: 1px 1px 2px black;
}
    </style>
    """, unsafe_allow_html=True
)

    year = st.selectbox("Select Year", [1, 2, 3])
    dept = st.selectbox("Select Department", ["CSE", "IT", "ECE"])
    section = st.selectbox("Select Section", ["A", "B", "C", "D", "E", "F"])
    if st.button("Generate Timetable"):
        batch = get_batch(year, dept, section)
        if not batch:
            st.error("⚠️ Batch not found in database!")
        else:
            timetable = generate_timetable(batch)
            if not timetable:
                st.warning("⚠️ No subjects/faculty found for this batch!")
            else:
                df = pd.DataFrame.from_dict(timetable, orient="index", columns=PERIODS)
                st.success(f"✅ Timetable generated for {dept} Year {year} Section {section}")
                st.dataframe(df.style.applymap(color_subjects), use_container_width=True)
                st.download_button(
                    label="📥 Download Timetable as Excel",
                    data=download_timetable(df),
                    file_name=f"{dept}_Y{year}_{section}_timetable.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

elif page == "Teacher":
    render_title("Teacher")
    st.markdown(
    """
    <style>
    .main-title {
      font-size: 64px;
      font-weight: 900;
      color: #FFD700;
      text-align: center;
      font-family: "Copperplate Gothic Bold", "Copperplate", "Copperplate Gothic", serif;
      width: 100%;
      padding: 20px 0;
      text-shadow: 2px 2px 6px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True
)
    st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://www.pomona.edu/sites/default/files/styles/16x9_1600_x_900/public/2022-08/algebra-classroom-from-behind.jpg?h=c44fcfa1&itok=o1bSoiLB");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }
    </style>
    """, unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.markdown(
    """
    <style>
    label {
    color: #FFD700 !important;
    font-weight: bold;
    font-size: 24px;
    text-shadow: 1px 1px 2px black;
}
    </style>
    """, unsafe_allow_html=True
)
        username = st.text_input("Username (Teacher ID)")
        password = st.text_input("Password (Dept)", type="password")
        login_btn = st.button("Login", use_container_width=True)
    if login_btn:
        teacher = get_teacher(username, password)
        if not teacher:
            st.error("❌ Invalid Teacher credentials")
        else:
            timetable = generate_teacher_timetable(teacher["teacher_id"])
            if not timetable:
                st.warning("⚠️ No classes assigned for this teacher!")
            else:
                df = pd.DataFrame.from_dict(timetable, orient="index", columns=PERIODS)
                st.success(f"✅ Timetable for {teacher['name']} ({teacher['dept']})")
                st.dataframe(df.style.applymap(color_subjects), use_container_width=True)
                st.download_button(
                    label="📥 Download Timetable as Excel",
                    data=download_timetable(df),
                    file_name=f"{teacher['name']}_timetable.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

elif page == "Admin":
    if st.session_state.logged_in:
        admin_panel()
    else:
        admin_login()
