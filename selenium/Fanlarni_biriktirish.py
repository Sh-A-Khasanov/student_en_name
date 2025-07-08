#######################################################################
#   student_list talabalarini fanga biriktirish. 
#######################################################################

import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.alert import Alert
import json


options = webdriver.ChromeOptions()
options.add_argument("--log-level=3")  # Faqat muhim xatolar chiqadi

driver = webdriver.Chrome(options=options)
driver.maximize_window()

# config.json faylini ochamiz va o‘qiymiz
with open("config.json", "r") as file:
    config = json.load(file)
# JSON fayldan URL ni olib ishlatamiz
driver.get(config["otm_url"])  



# JSON faylni ochish va o'qish
with open("config.json", "r") as file:
    config = json.load(file)
login_value = config["login"]
parol_value = config["parol"]


login = driver.find_element(By.NAME, "FormAdminLogin[login]")
# login.clear()
login.send_keys(login_value)
parol = driver.find_element(By.NAME, "FormAdminLogin[password]")
# login.clear()
parol.send_keys(parol_value)
time.sleep(10)

db_name = config["db_name"]
# SQLite bazaga ulanish
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Talabalar ro'yxatini olish
cursor.execute("SELECT id, education_year_code, department_id, education_type_code, curriculum_id, semester_code, group_id, education_form_code FROM student_list")
students = cursor.fetchall()
conn.close()

# Har bir talaba uchun URL yaratish va unga o'tish
for student in students:
    time.sleep(1)
    student_id, education_year_code, department_id, education_type_code, curriculum_id, semester_code, group_id, education_form_code = map(str, student)

    url = (
        f"{config['otm_url']}/curriculum/student-subjects-register?"
        f"EStudentSubjectsRegister%5B_education_year%5D={education_year_code}&"
        f"EStudentSubjectsRegister%5B_department%5D={department_id}&"
        f"EStudentSubjectsRegister%5B_education_type%5D={education_type_code}&"
        f"EStudentSubjectsRegister%5B_education_form%5D={education_form_code}&"
        f"EStudentSubjectsRegister%5B_curriculum%5D={curriculum_id}&"
        f"EStudentSubjectsRegister%5B_semester%5D={semester_code}&"
        f"EStudentSubjectsRegister%5B_group%5D={group_id}&"
        f"EStudentSubjectsRegister%5B_student%5D={student_id}&"
        f"_pjax=%23admin-grid"
    )

    print(f"\nTalaba {student_id} uchun sahifa ochilmoqda...")
    driver.get(url)
    time.sleep(0.5)  # Sayt to'liq yuklanishi uchun kutish
    
    
    
    # rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
    # print("TR & Fanlar soni:", len(rows))
    # tanlov_soni = 0
    # for tr_soni in range(1, (len(rows))+1):
    #     # time.sleep(2)
    #     fan_turi = driver.find_element(By.XPATH, "/html/body/div/div[2]/section[2]/div/form/div/div[2]/div/div[1]/div[1]/table/tbody/tr["+str(tr_soni)+"]/td[4]")
    #     fan_nomi = driver.find_element(By.XPATH, "/html/body/div/div[2]/section[2]/div/form/div/div[2]/div/div[1]/div[1]/table/tbody/tr["+str(tr_soni)+"]/td[2]").text
        
    #     if fan_turi.text.strip() == "Tanlov":
    #         tanlov_soni += 1
    #         # Checkbox elementini topish
    #         checkbox = driver.find_element(By.CLASS_NAME, "select-on-check-all")
    #         checkbox.click()
    #         Fanni_biriktirish = driver.find_element(By.ID, "assign")
    #         Fanni_biriktirish.click()
    #         # time.sleep(2)
    #         # Alert oynasini aniqlash va "OK" tugmasini bosish
    #         alert = Alert(driver)
    #         alert.accept()  
    #         print(f"{tanlov_soni} Biriktirildi:", fan_nomi)
    # print("Tanlov fanlar soni:", tanlov_soni)
    
    
    
    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
    print("Fanlar soni:", len(rows))

    guruhlar_biriktirilgan = set()
    checkboxlar_soni = 0

    for row in rows:
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 7:
                continue

            fan_nomi = cells[1].text.strip()
            fan_guruh = cells[6].text.strip()
            checkbox = row.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')

            is_disabled = checkbox.get_attribute("disabled") is not None

            # 1. Agar disabled bo‘lsa — bu fan allaqachon biriktirilgan
            if is_disabled:
                if fan_guruh:
                    guruhlar_biriktirilgan.add(fan_guruh)
                print(f"🔒 Biriktirilgan fan: {fan_nomi} | Guruh: {fan_guruh}")
                continue

            # 2. Enabled va hali biriktirilmagan guruh bo‘lsa — tanlaymiz
            if fan_guruh and fan_guruh in guruhlar_biriktirilgan:
                print(f"❌ Guruh {fan_guruh} allaqachon tanlangan: {fan_nomi} o'tkazildi.")
                continue

            checkbox.click()
            checkboxlar_soni += 1
            print(f"✅ Belgilandi: {fan_nomi}")
            if fan_guruh:
                guruhlar_biriktirilgan.add(fan_guruh)

        except Exception as e:
            print(f"❌ Xatolik: {str(e)}")

    # Oxirida faqat 1 marta biriktirish
    if checkboxlar_soni > 0:
        try:
            driver.find_element(By.ID, "assign").click()
            Alert(driver).accept()
            print(f"\n✅ Jami {checkboxlar_soni} fan biriktirildi.")
        except Exception as e:
            print(f"❌ Biriktirishda xatolik: {str(e)}")
    else:
        print("ℹ️ Belgilangan fan yo‘q.")










print("Barcha sahifalar ochildi!")
driver.quit()
