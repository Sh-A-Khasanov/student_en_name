###############################################################
#   hemis_api.db sqlitega student-list tableda barcha 
#   talabalarning ID laridan foydalanib parollarini default
#   xolatga qaytaradi.
###############################################################

import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json


# Selenium sozlamalari
options = webdriver.ChromeOptions()
options.add_argument("--log-level=3")  # Faqat muhim xatolar chiqadi
driver = webdriver.Chrome(options=options)
driver.maximize_window()

# config.json faylini o‘qiymiz
with open("config.json", "r") as file:
    config = json.load(file)

driver.get(config["otm_url"])  
 
# Login va parolni kiritish
login_value = config["login"]
parol_value = config["parol"]

login = driver.find_element(By.NAME, "FormAdminLogin[login]")
login.send_keys(login_value)
parol = driver.find_element(By.NAME, "FormAdminLogin[password]")
parol.send_keys(parol_value)
time.sleep(15)  # Sayt yuklanishini kutish va kirish tugmasini bosish uchun vaqt

db_name = config["db_name"]
# Ma'lumotlar bazasiga ulanish
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Talabalar ro'yxatini olish
cursor.execute("SELECT id FROM student_list")
students = cursor.fetchall()
conn.close()

print(f"Jami Talaba_ID lar soni: {len(students)}")

for student in students:
    student_id = str(student[0])
    url = f"{config['otm_url']}student/student-edit?id={student_id}&reset=1"
    driver.get(url)
    time.sleep(0.5)
print("✅ Barcha Parollar tiklandi")
driver.quit()
