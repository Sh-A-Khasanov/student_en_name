###############################################################
#   O'quv rejaga tegishli fanlar ro'yxatini apidan
#   keladigan barcha malumotlarni olib bazaga yoz bazaga yozadi 
###############################################################

import requests
import sqlite3
import time
import json
from datetime import datetime, timedelta, timezone

# config.json faylidan API ma'lumotlarini yuklash
with open("config.json", "r") as file:
    config = json.load(file)

BASE_URL  = f"{config['student_otm_url']}rest/v1/data/curriculum-subject-list"
api_key = config["api_key"]
HEADERS  = {"Authorization": f"Bearer {api_key}"}


# SQLite bazaga ulanish
db_name = config["db_name"]
# SQLite bazaga ulanish
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Jadval yaratish
cursor.execute('''
CREATE TABLE IF NOT EXISTS curriculum_subject_list (
    id INTEGER PRIMARY KEY,
    subject_id INTEGER,
    subject_name TEXT,
    subject_code TEXT,
    subject_type_code TEXT,
    subject_type_name TEXT,
    subject_block_code TEXT,
    subject_block_name TEXT,
    training_type_code TEXT,
    training_type_name TEXT,
    academic_load INTEGER,
    exam_type_code TEXT,
    exam_type_name TEXT,
    max_ball INTEGER,
    rating_grade_code TEXT,
    rating_grade_name TEXT,
    exam_finish_code TEXT,
    exam_finish_name TEXT,
    department_id INTEGER,
    department_name TEXT,
    department_code TEXT,
    department_structure_type_code TEXT,
    department_structure_type_name TEXT,
    department_locality_type_code TEXT,
    department_locality_type_name TEXT,
    department_parent INTEGER,
    department_active BOOLEAN,
    semester_code TEXT,
    semester_name TEXT,
    curriculum_id INTEGER,
    total_acload INTEGER,
    resource_count INTEGER,
    in_group TEXT,
    at_semester BOOLEAN,
    active BOOLEAN,
    credit INTEGER,
    created_at DATETIME,
    updated_at DATETIME,
    status_api TINYINT DEFAULT 0
)
''')
conn.commit()

def fetch_data(page):
    """API'dan ma'lumot olish"""
    params = {"page": page, "limit": 200}
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def fetch_and_store_subjects():
    """Ma'lumotlarni API'dan yuklab, SQLite bazasiga saqlash"""
    page = 1
    data = fetch_data(page)
    
    if not data:
        print("❌ Ma'lumotni olishda xatolik yuz berdi.")
        return
    
    page_count = data.get("data", {}).get("pagination", {}).get("pageCount", 1)
    print(f"📌 Jami sahifalar soni: {page_count}")
    
    while page <= page_count:
        print(f"🔄 {page} - ma'lumot olinmoqda...")
        data = fetch_data(page)
        
        if not data:
            print(f"‼️ {page} - Maʼlumot yoʻq yoki xatolik yuz berdi")
            time.sleep(2)
            continue
        
        items = data.get("data", {}).get("items", [])
        for item in items:
            raw_created_at = item.get("created_at")
            # created_at = (datetime.utcfromtimestamp(raw_created_at) + timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S')
            raw_updated_at = item.get("updated_at")
            # updated_at = (datetime.utcfromtimestamp(raw_updated_at) + timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S')

            created_at = datetime.fromtimestamp(item.get("created_at", 0), timezone.utc) + timedelta(hours=5)
            updated_at = datetime.fromtimestamp(item.get("updated_at", 0), timezone.utc) + timedelta(hours=5)

            cursor.execute('''
            INSERT INTO curriculum_subject_list (
                    id, subject_id, subject_name, subject_code, subject_type_code, subject_type_name,
                    subject_block_code, subject_block_name, training_type_code, training_type_name,
                    academic_load, exam_type_code, exam_type_name, max_ball, rating_grade_code,
                    rating_grade_name, exam_finish_code, exam_finish_name, department_id,
                    department_name, department_code, department_structure_type_code,
                    department_structure_type_name, department_locality_type_code,
                    department_locality_type_name, department_parent, department_active,
                    semester_code, semester_name, curriculum_id, total_acload, resource_count,
                    in_group, at_semester, active, credit, created_at, updated_at, status_api
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.get("id"),
                    item.get("subject", {}).get("id") if item.get("subject") else None,
                    item.get("subject", {}).get("name") if item.get("subject") else None,
                    item.get("subject", {}).get("code") if item.get("subject") else None,
                    item.get("subjectType", {}).get("code") if item.get("subjectType") else None,
                    item.get("subjectType", {}).get("name") if item.get("subjectType") else None,
                    item.get("subjectBlock", {}).get("code") if item.get("subjectBlock") else None,
                    item.get("subjectBlock", {}).get("name") if item.get("subjectBlock") else None,
                    item.get("subjectDetails", [{}])[0].get("trainingType", {}).get("code") if item.get("subjectDetails") else None,
                    item.get("subjectDetails", [{}])[0].get("trainingType", {}).get("name") if item.get("subjectDetails") else None,
                    item.get("subjectDetails", [{}])[0].get("academic_load") if item.get("subjectDetails") else None,
                    item.get("subjectExamTypes", [{}])[0].get("examType", {}).get("code") if item.get("subjectExamTypes") else None,
                    item.get("subjectExamTypes", [{}])[0].get("examType", {}).get("name") if item.get("subjectExamTypes") else None,
                    item.get("subjectExamTypes", [{}])[0].get("max_ball") if item.get("subjectExamTypes") else None,
                    item.get("ratingGrade", {}).get("code") if item.get("ratingGrade") else None,
                    item.get("ratingGrade", {}).get("name") if item.get("ratingGrade") else None,
                    item.get("examFinish", {}).get("code") if item.get("examFinish") else None,
                    item.get("examFinish", {}).get("name") if item.get("examFinish") else None,
                    item.get("department", {}).get("id") if item.get("department") else None,
                    item.get("department", {}).get("name") if item.get("department") else None,
                    item.get("department", {}).get("code") if item.get("department") else None,
                    item.get("department", {}).get("structureType", {}).get("code") if item.get("department") else None,
                    item.get("department", {}).get("structureType", {}).get("name") if item.get("department") else None,
                    item.get("department", {}).get("localityType", {}).get("code") if item.get("department") else None,
                    item.get("department", {}).get("localityType", {}).get("name") if item.get("department") else None,
                    item.get("department", {}).get("parent") if item.get("department") else None,
                    item.get("department", {}).get("active") if item.get("department") else None,
                    item.get("semester", {}).get("code") if item.get("semester") else None,
                    item.get("semester", {}).get("name") if item.get("semester") else None,
                    item.get("_curriculum") if item.get("_curriculum") else None,
                    item.get("total_acload") if item.get("total_acload") else None,
                    item.get("resource_count") if item.get("resource_count") else None,
                    item.get("in_group") if item.get("in_group") else None,
                    item.get("at_semester") if item.get("at_semester") else None,
                    item.get("active") if item.get("active") else None,
                    item.get("credit") if item.get("credit") else None,
                    created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    1
            ))
        
        conn.commit()
        # print(f"✅ {page} - sahifa yuklandi.")
        page += 1

    print(f"✅ Barcha {page_count} sahifa yuklandi.")

fetch_and_store_subjects()

# Ulanuvchi yopiladi
conn.close()
print("Barcha ma'lumotlar bazaga yozildi.")
