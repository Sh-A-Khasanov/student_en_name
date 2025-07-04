###############################################################
# Bazadaki talabalarni diplom ilovasiga chiqaradigan F.I.O larni 
# transliterate funksyasi tartibda inglizcha o'zgartirib chiqadi
###############################################################

import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.alert import Alert
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re  # Regex uchun

# Transliteration funksiyasi
def transliterate(name):
    name = re.sub(r"YEV", "EV", name)  # YEV → EV
    name = re.sub(r"’", "", name)  # Apostrofni olib tashlash
    name = re.sub(r"O‘", "U", name)  # O‘ → U
    name = re.sub(r"G‘", "G", name)  # G‘ → G
    name = re.sub(r"Q", "K", name)  # Q → K
    name = re.sub(r"(?<![SCK])H", "KH", name)  # H → KH (S, C, K dan keyin bo‘lmasa)
    name = re.sub(r"X", "KH", name)  # X → KH
    return name



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


# Har bir talaba uchun sahifani ochish va ma'lumotlarni yangilash


print(f"Jami ID lar soni: {len(students)}")



log_file = "log_en_student.txt"  # Log fayl nomi




for student in students:
    student_id = str(student[0])

    url = f"{config['otm_url']}en/student/student-passport-edit?id={student_id}"
    driver.get(url)
    print(f"Talaba {student_id} uchun sahifa ochilmoqda...")
    while True:
        try:
            # Sahifa yuklanishini kutish
            wait = WebDriverWait(driver, 10)  # Maksimum 10 soniya kutish
            value = wait.until(EC.presence_of_element_located((By.ID, "passport_number")))

            # Elementning `value` atributini olish
            passport_number = value.get_attribute("value")

            # Input elementini ID orqali topish
            passport_input = driver.find_element(By.ID, "passport_number")
            # Avval eski qiymatni o'chirish
            passport_input.clear()
            # Yangi qiymatni kiritish
            passport_input.send_keys("AA1234567")

            saqlash = driver.find_element(By.XPATH, "//button[@type='submit']")
            saqlash.click()
            # time.sleep(2)
            break
        except:
            print("qayta - 1")
    while True:
        try:
            # Ism va familiyani olish
            second_name_h = driver.find_element(By.ID, "second_name").get_attribute("value")
            first_name_h = driver.find_element(By.ID, "first_name").get_attribute("value")
            
            # Transliteration qilish
            new_second_name = transliterate(second_name_h)
            new_first_name = transliterate(first_name_h)

            # Agar o‘zgarish bo‘lsa, yangilash
            if new_second_name != second_name_h:
                second_name_input = driver.find_element(By.ID, "second_name")
                second_name_input.clear()
                second_name_input.send_keys(new_second_name)
                print(f"✅ {second_name_h} → {new_second_name}")

            if new_first_name != first_name_h:
                first_name_input = driver.find_element(By.ID, "first_name")
                first_name_input.clear()
                first_name_input.send_keys(new_first_name)
                
                # Sahifa yuklanishini kutish
            wait = WebDriverWait(driver, 10)  # Maksimum 10 soniya kutish
            third_name_input = wait.until(EC.presence_of_element_located((By.ID, "third_name")))

            # third_name_input = driver.find_element(By.ID, "third_name")
            third_name_input.clear()

            # Elementni ID orqali topish va value ni olish
            passport_number1 = driver.find_element(By.ID, "passport_number")
            passport_number1.clear()
            passport_number1.send_keys(passport_number)
            saqlash = driver.find_element(By.XPATH, "//button[@type='submit']")
            saqlash.click()
        # print(passport_number)
            time.sleep(1)
            break
        except:
            print("qayta - 2")
print("Barcha sahifalar ochildi!")
driver.quit()


 
# # Talaba ID sini log.txt ga yozish (yozib borish rejimi 'a')
# with open(log_file, "a", encoding="utf-8") as log:
#     log.write(student_id + "\n")