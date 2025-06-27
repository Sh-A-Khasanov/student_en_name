import requests
# pip install mysql-connector-python
import time
import json
from datetime import datetime, timedelta, timezone
import sqlite3

# config.json faylidan API ma'lumotlarini yuklash
with open("config.json", "r") as file:
    config = json.load(file)

BASE_URL = f"{config['student_otm_url']}rest/v1/data/student-list"  # API manzili
api_key = config["api_key"]
HEADERS = {"Authorization": f"Bearer {api_key}"}

# MySQL bazaga ulanish
# SQLite bazaga ulanish
conn = sqlite3.connect("hemis_api.db")
cursor = conn.cursor()


# Jadval yaratish (status_api ustuni qo'shildi)
cursor.execute('''
CREATE TABLE IF NOT EXISTS student_list (
    id INTEGER PRIMARY KEY,
    meta_id INTEGER,
    university_code VARCHAR(50),
    university_name VARCHAR(255),
    full_name VARCHAR(255),
    short_name VARCHAR(100),
    first_name VARCHAR(100),
    second_name VARCHAR(100),
    third_name VARCHAR(100),
    gender_code VARCHAR(10),
    gender_name VARCHAR(50),
    birth_date DATE,
    student_id_number VARCHAR(50),
    image TEXT,
    avg_gpa FLOAT,
    avg_grade FLOAT,
    total_credit INTEGER,
    country_code VARCHAR(10),
    country_name VARCHAR(100),
    province_code VARCHAR(10),
    province_name VARCHAR(100),
    current_province_code VARCHAR(10),
    current_province_name VARCHAR(100),
    district_code VARCHAR(10),
    district_name VARCHAR(100),
    current_district_code VARCHAR(10),
    current_district_name VARCHAR(100),
    terrain_code VARCHAR(10),
    terrain_name VARCHAR(100),
    current_terrain_code VARCHAR(10),
    current_terrain_name VARCHAR(100),
    citizenship_code VARCHAR(10),
    citizenship_name VARCHAR(100),
    student_status_code VARCHAR(10),
    student_status_name VARCHAR(100),
    curriculum_id INTEGER,
    education_form_code VARCHAR(10),
    education_form_name VARCHAR(100),
    education_type_code VARCHAR(10),
    education_type_name VARCHAR(100),
    payment_form_code VARCHAR(10),
    payment_form_name VARCHAR(100),
    student_type_code VARCHAR(10),
    student_type_name VARCHAR(100),
    social_category_code VARCHAR(10),
    social_category_name VARCHAR(100),
    accommodation_code VARCHAR(10),
    accommodation_name VARCHAR(100),
    department_id INTEGER,
    department_code VARCHAR(50),
    department_name VARCHAR(255),
    department_structure_type_code VARCHAR(10),
    department_structure_type_name VARCHAR(100),
    department_locality_type_code VARCHAR(10),
    department_locality_type_name VARCHAR(100),
    department_parent INTEGER,
    department_active TINYINT(1),
    specialty_id INTEGER,
    specialty_code VARCHAR(50),
    specialty_name VARCHAR(255),
    group_id INTEGER,
    group_name VARCHAR(100),
    education_lang_code VARCHAR(10),
    education_lang_name VARCHAR(100),
    level_code VARCHAR(10),
    level_name VARCHAR(100),
    semester_id INTEGER,
    semester_code VARCHAR(10),
    semester_name VARCHAR(100),
    education_year_code VARCHAR(10),
    education_year_name VARCHAR(100),
    education_year_current TINYINT(1),
    year_of_enter INTEGER,
    roommate_count INTEGER,
    is_graduate TINYINT(1),
    total_acload INTEGER,
    other TEXT,
    created_at DATETIME,
    updated_at DATETIME,
    hash VARCHAR(255),
    validate_url TEXT,
    status_api TINYINT DEFAULT 0
)
''')
conn.commit()


def fetch_data(page):
    """API'dan ma'lumot olish"""
    # params = {"page": page, "limit": 200, "_student_status": 11,"_curriculum":67 }
    params = {"page": page, "limit": 200, "_student_status": -1 }
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    return None


# Unix timestamp-ni YYYY-MM-DD formatiga aylantirish funksiyasi
def to_mysql_date(unix_timestamp):
    try:
        if unix_timestamp is not None:
            timestamp = int(unix_timestamp)
            epoch = datetime(1970, 1, 1)
            date = epoch + timedelta(seconds=timestamp)
            return date.strftime('%Y-%m-%d')
        else:
            return None
    except (ValueError, TypeError, OSError) as e:
        print(f"❌ Xatolik: {e}")
        return None








def fetch_and_store_students():
    cursor.execute("UPDATE student_list SET status_api = 0 WHERE status_api = 1;")
    conn.commit()
    print("⭕️ Barcha status_api qiymatlari 0 ga o'rnatildi.")

    page = 1
    data = fetch_data(page)

    if not data:
        print("❌ Ma'lumotni olishda xatolik yuz berdi.")
        return

    try:
        data_content = data.get("data", {})
        pagination = data_content.get("pagination", {})
        page_count = pagination.get("pageCount", 1)
    except (IndexError, KeyError) as e:
        print(f"❌ Pagination ma'lumotlarini olishda xato: {e}")
        page_count = 1

    print(f"🙍🏻‍♂️ Jami sahifalar soni: {page_count}")

    while page <= page_count:
        data = fetch_data(page)
        if not data:
            print(f"‼️ {page} - sahifa yuklab bo‘lmadi")
            time.sleep(2)
            continue

        items = data.get("data", {}).get("items", [])

        for item in items:
            created_at = datetime.fromtimestamp(item.get("created_at", 0), timezone.utc) + timedelta(hours=5)
            updated_at = datetime.fromtimestamp(item.get("updated_at", 0), timezone.utc) + timedelta(hours=5)
            birth_date = to_mysql_date(item.get("birth_date"))

            values = (
                item.get("id"),
                item.get("meta_id"),
                item.get("university", {}).get("code"),
                item.get("university", {}).get("name"),
                item.get("full_name"),
                item.get("short_name"),
                item.get("first_name"),
                item.get("second_name"),
                item.get("third_name"),
                item.get("gender", {}).get("code"),
                item.get("gender", {}).get("name"),
                birth_date,
                item.get("student_id_number"),
                item.get("image"),
                item.get("avg_gpa"),
                item.get("avg_grade"),
                item.get("total_credit"),
                item.get("country", {}).get("code"),
                item.get("country", {}).get("name"),
                item.get("province", {}).get("code"),
                item.get("province", {}).get("name"),
                item.get("currentProvince", {}).get("code") if item.get("currentProvince") else None,
                item.get("currentProvince", {}).get("name") if item.get("currentProvince") else None,
                item.get("district", {}).get("code"),
                item.get("district", {}).get("name"),
                item.get("currentDistrict", {}).get("code") if item.get("currentDistrict") else None,
                item.get("currentDistrict", {}).get("name") if item.get("currentDistrict") else None,
                item.get("terrain", {}).get("code") if item.get("terrain") else None,
                item.get("terrain", {}).get("name") if item.get("terrain") else None,
                item.get("currentTerrain", {}).get("code") if item.get("currentTerrain") else None,
                item.get("currentTerrain", {}).get("name") if item.get("currentTerrain") else None,
                item.get("citizenship", {}).get("code"),
                item.get("citizenship", {}).get("name"),
                item.get("studentStatus", {}).get("code"),
                item.get("studentStatus", {}).get("name"),
                item.get("_curriculum"),
                item.get("educationForm", {}).get("code") if item.get("educationForm") else None,
                item.get("educationForm", {}).get("name") if item.get("educationForm") else None,
                item.get("educationType", {}).get("code"),
                item.get("educationType", {}).get("name"),
                item.get("paymentForm", {}).get("code"),
                item.get("paymentForm", {}).get("name"),
                item.get("studentType", {}).get("code"),
                item.get("studentType", {}).get("name"),
                item.get("socialCategory", {}).get("code"),
                item.get("socialCategory", {}).get("name"),
                item.get("accommodation", {}).get("code"),
                item.get("accommodation", {}).get("name"),
                item.get("department", {}).get("id"),
                item.get("department", {}).get("code"),
                item.get("department", {}).get("name"),
                item.get("department", {}).get("structureType", {}).get("code"),
                item.get("department", {}).get("structureType", {}).get("name"),
                item.get("department", {}).get("localityType", {}).get("code"),
                item.get("department", {}).get("localityType", {}).get("name"),
                item.get("department", {}).get("parent"),
                item.get("department", {}).get("active"),
                item.get("specialty", {}).get("id"),
                item.get("specialty", {}).get("code"),
                item.get("specialty", {}).get("name"),
                item.get("group", {}).get("id") if item.get("group") else None,
                item.get("group", {}).get("name") if item.get("group") else None,
                item.get("group", {}).get("educationLang", {}).get("code") if item.get("group") else None,
                item.get("group", {}).get("educationLang", {}).get("name") if item.get("group") else None,
                item.get("level", {}).get("code") if item.get("level") else None,
                item.get("level", {}).get("name") if item.get("level") else None,
                item.get("semester", {}).get("id"),
                item.get("semester", {}).get("code"),
                item.get("semester", {}).get("name"),
                item.get("educationYear", {}).get("code") if item.get("educationYear") else None,
                item.get("educationYear", {}).get("name") if item.get("educationYear") else None,
                item.get("educationYear", {}).get("current") if item.get("educationYear") else None,
                item.get("year_of_enter"),
                item.get("roommate_count"),
                item.get("is_graduate"),
                item.get("total_acload"),
                item.get("other"),
                created_at.strftime('%Y-%m-%d %H:%M:%S'),
                updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                item.get("hash"),
                item.get("validateUrl"),
                1
            )

            cursor.execute('''
INSERT INTO student_list (
    id, meta_id, university_code, university_name, full_name, short_name,
    first_name, second_name, third_name, gender_code, gender_name,
    birth_date, student_id_number, image, avg_gpa, avg_grade, total_credit,
    country_code, country_name, province_code, province_name,
    current_province_code, current_province_name, district_code, district_name,
    current_district_code, current_district_name, terrain_code, terrain_name,
    current_terrain_code, current_terrain_name, citizenship_code, citizenship_name,
    student_status_code, student_status_name, curriculum_id,
    education_form_code, education_form_name, education_type_code, education_type_name,
    payment_form_code, payment_form_name, student_type_code, student_type_name,
    social_category_code, social_category_name, accommodation_code, accommodation_name,
    department_id, department_code, department_name,
    department_structure_type_code, department_structure_type_name,
    department_locality_type_code, department_locality_type_name,
    department_parent, department_active,
    specialty_id, specialty_code, specialty_name,
    group_id, group_name, education_lang_code, education_lang_name,
    level_code, level_name, semester_id, semester_code, semester_name,
    education_year_code, education_year_name, education_year_current,
    year_of_enter, roommate_count, is_graduate, total_acload, other,
    created_at, updated_at, hash, validate_url, status_api
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(id) DO UPDATE SET
    meta_id=excluded.meta_id,
    university_code=excluded.university_code,
    university_name=excluded.university_name,
    full_name=excluded.full_name,
    short_name=excluded.short_name,
    first_name=excluded.first_name,
    second_name=excluded.second_name,
    third_name=excluded.third_name,
    gender_code=excluded.gender_code,
    gender_name=excluded.gender_name,
    birth_date=excluded.birth_date,
    student_id_number=excluded.student_id_number,
    image=excluded.image,
    avg_gpa=excluded.avg_gpa,
    avg_grade=excluded.avg_grade,
    total_credit=excluded.total_credit,
    country_code=excluded.country_code,
    country_name=excluded.country_name,
    province_code=excluded.province_code,
    province_name=excluded.province_name,
    current_province_code=excluded.current_province_code,
    current_province_name=excluded.current_province_name,
    district_code=excluded.district_code,
    district_name=excluded.district_name,
    current_district_code=excluded.current_district_code,
    current_district_name=excluded.current_district_name,
    terrain_code=excluded.terrain_code,
    terrain_name=excluded.terrain_name,
    current_terrain_code=excluded.current_terrain_code,
    current_terrain_name=excluded.current_terrain_name,
    citizenship_code=excluded.citizenship_code,
    citizenship_name=excluded.citizenship_name,
    student_status_code=excluded.student_status_code,
    student_status_name=excluded.student_status_name,
    curriculum_id=excluded.curriculum_id,
    education_form_code=excluded.education_form_code,
    education_form_name=excluded.education_form_name,
    education_type_code=excluded.education_type_code,
    education_type_name=excluded.education_type_name,
    payment_form_code=excluded.payment_form_code,
    payment_form_name=excluded.payment_form_name,
    student_type_code=excluded.student_type_code,
    student_type_name=excluded.student_type_name,
    social_category_code=excluded.social_category_code,
    social_category_name=excluded.social_category_name,
    accommodation_code=excluded.accommodation_code,
    accommodation_name=excluded.accommodation_name,
    department_id=excluded.department_id,
    department_code=excluded.department_code,
    department_name=excluded.department_name,
    department_structure_type_code=excluded.department_structure_type_code,
    department_structure_type_name=excluded.department_structure_type_name,
    department_locality_type_code=excluded.department_locality_type_code,
    department_locality_type_name=excluded.department_locality_type_name,
    department_parent=excluded.department_parent,
    department_active=excluded.department_active,
    specialty_id=excluded.specialty_id,
    specialty_code=excluded.specialty_code,
    specialty_name=excluded.specialty_name,
    group_id=excluded.group_id,
    group_name=excluded.group_name,
    education_lang_code=excluded.education_lang_code,
    education_lang_name=excluded.education_lang_name,
    level_code=excluded.level_code,
    level_name=excluded.level_name,
    semester_id=excluded.semester_id,
    semester_code=excluded.semester_code,
    semester_name=excluded.semester_name,
    education_year_code=excluded.education_year_code,
    education_year_name=excluded.education_year_name,
    education_year_current=excluded.education_year_current,
    year_of_enter=excluded.year_of_enter,
    roommate_count=excluded.roommate_count,
    is_graduate=excluded.is_graduate,
    total_acload=excluded.total_acload,
    other=excluded.other,
    created_at=excluded.created_at,
    updated_at=excluded.updated_at,
    hash=excluded.hash,
    validate_url=excluded.validate_url,
    status_api=1
''', values)

        conn.commit()
        print(f"✅ {page} - sahifa yuklandi.")
        page += 1

    print(f"✅ Barcha {page_count} sahifa yuklandi.")

fetch_and_store_students()

# Ulanishni yopish
conn.close()
print("Barcha ma'lumotlar bazaga yozildi.")
# if __name__ == "__main__":
#     fetch_and_store_students()























