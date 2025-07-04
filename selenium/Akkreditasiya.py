#######################################################################
#   curriculum_subject_list.py va student_list.py fayllarini 
#   ishga tushirgandan keyin bazadaki shu malumotlardan foydalanib
#   `Akkreditasiyadaki` talabalarning fan soatlarini to'g'rilab  chiqadi
#######################################################################



import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json

# Brauzer sozlamalari
options = webdriver.ChromeOptions()
options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=options)
driver.maximize_window()

# config.json o‘qish
with open("config.json", "r") as file:
    config = json.load(file)

# Kirish sahifasini ochish
driver.get(config["otm_url"])
login = driver.find_element(By.NAME, "FormAdminLogin[login]")
login.send_keys(config["login"])
parol = driver.find_element(By.NAME, "FormAdminLogin[password]")
parol.send_keys(config["parol"])
time.sleep(10)

# Bazaga ulanish
db_name = config["db_name"]
# Ma'lumotlar bazasiga ulanish
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Talaba va fanlarni bog‘lash
query = """
SELECT
    sl.id AS student_id,
    sl.meta_id,
    sl.curriculum_id,
    csl.id AS subject_id,
    csl.total_acload,
    csl.credit
FROM student_list sl
LEFT JOIN curriculum_subject_list csl ON sl.curriculum_id = csl.curriculum_id
"""

cursor.execute(query)
rows = cursor.fetchall()

for row in rows:
    student_id = row[0]
    meta_id = row[1]
    curriculum_id = row[2]
    subject_id = row[3]
    total_acload = row[4]
    credit = row[5]

    print(f"Student ID: {student_id}, Meta ID: {meta_id}, Subject ID: {subject_id}, Acload: {total_acload}, Credit: {credit}")

    url = f"{config['otm_url']}archive/accreditation-view?id={meta_id}&subject={subject_id}&rating=1"
    driver.get(url)

    try:
        credit_input = driver.find_element(By.NAME, "EAcademicRecord[credit]")
        credit_input.clear()
        credit_input.send_keys(str(credit))

        acload_input = driver.find_element(By.NAME, "EAcademicRecord[total_acload]")
        acload_input.clear()
        acload_input.send_keys(str(total_acload))

        save_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        save_button.click()
        time.sleep(0.5)

    except Exception as e:
        with open("errors.txt", "a", encoding="utf-8") as f:
            f.write(f"Xatolik: student_id={student_id}, meta_id={meta_id}, subject_id={subject_id}, acload={total_acload}, credit={credit}\n")
        continue

conn.close()
























































# # bazadaki o'quv reja  fan silabuslari malumotini akreditatsiyadan to'g'rilab chiqish



# import sqlite3
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# import time
# import json


# # google chrome orqali ishlaydi 
# options = webdriver.ChromeOptions()
# options.add_argument("--log-level=3")  # Faqat muhim xatolar chiqadi

# driver = webdriver.Chrome(options=options)
# driver.maximize_window()

# # config.json faylini ochamiz va o‘qiymiz
# with open("config.json", "r") as file:
#     config = json.load(file)
# # JSON fayldan URL ni olib ishlatamiz
# driver.get(config["otm_url"])  


# # JSON faylni ochish va o'qish
# with open("config.json", "r") as file:
#     config = json.load(file)
# login_value = config["login"]
# parol_value = config["parol"]


# login = driver.find_element(By.NAME, "FormAdminLogin[login]")
# # login.clear()
# login.send_keys(login_value)
# parol = driver.find_element(By.NAME, "FormAdminLogin[password]")
# # login.clear()
# parol.send_keys(parol_value)
# time.sleep(10)

# # Ma'lumotlar bazasiga ulanish
# conn = sqlite3.connect("hemis_api.db")
# cursor = conn.cursor()

# # curriculum_subject_list va student_listni curriculum_id ustuni bo‘yicha bog‘lab olish
# # query = """
# #     SELECT csl.id, csl.curriculum_id, csl.total_acload, csl.credit, sl.meta_id
# #     FROM curriculum_subject_list csl
# #     LEFT JOIN student_list sl ON csl.curriculum_id = sl.curriculum_id
# # """
# query = """
# SELECT
#     sl.id AS student_id,
#     sl.meta_id,
#     sl.curriculum_id,
#     csl.id AS subject_id,
#     csl.total_acload,
#     csl.credit
# FROM student_list sl
# LEFT JOIN curriculum_subject_list csl ON sl.curriculum_id = csl.curriculum_id

# """

# cursor.execute(query)
# rows = cursor.fetchall()

# # Natijalarni chiqarish

# for row in rows:
#     # print(rows)
#     print(f"ID: {row[0]}, Curriculum_ID: {row[1]}, Total Acload: {row[2]}, Credit: {row[3]}, Meta ID: {row[4]}")
#     url = f"{config['otm_url']}/archive/accreditation-view?id={row[3]}&subject={row[1]}&rating=1"
#     driver.get(url)   
#     try:
#         credit_input = driver.find_element(By.NAME, "EAcademicRecord[credit]")
#         credit_input.clear()
#         credit_input.send_keys(row[3])
#         total_acload = driver.find_element(By.NAME, "EAcademicRecord[total_acload]")
#         total_acload.clear()
#         total_acload.send_keys(row[2])

#         # Saqlash tugmachasini topish va bosish
#         save_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
#         save_button.click()
#         time.sleep(0.5)
#     except:
#         with open("errors.txt", "a", encoding="utf-8") as f:
#             f.write(f"Error ID: {row[0]}, Curriculum_ID: {row[1]}, Total Acload: {row[2]}, Credit: {row[3]}, Meta ID: {row[4]}\n")
#         pass
# # Ulashni yopish
# conn.close()












