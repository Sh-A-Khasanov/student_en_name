###############################################################
#   student_list ga tegishli bo`lgan talabalarning
#   curriculum_id, education_year_code, semester_code,
#   group_id lardan foydalanib barcha talabani fangab iriktiriadi
#   tanlov fanlar nechta bo`lsa shuncha marta biriktiradi
#   
#   driver.find_element(By.ID, "delete").click() izohga olingan
#   BU qismi xususiy OTMlar uchun qo'l keladi
#   guruh o`zgartrgan talabalarni oldn fanlarni o`chiradi
#   keyin qayta biriktiradi. Davlat OTMlarda perevod kam 
#   bo`lganligi sababli shart emas izohda tursin
###############################################################



import sqlite3
from selenium import webdriver
import time
from selenium.webdriver.common.alert import Alert
import json
import sys
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

boshlash_group_id = ""

class Logger:
    def __init__(self, fayl_nomi):
        self.konsol = sys.stdout
        self.fayl = open(fayl_nomi, 'a', encoding='utf-8')
    
    def write(self, xabar):
        self.konsol.write(xabar)
        self.fayl.write(xabar)
    
    def flush(self):
        self.konsol.flush()
        self.fayl.flush()
 
sys.stdout = Logger('log_Fanga_biriktirish.txt')

options = webdriver.ChromeOptions()
options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=options)
driver.maximize_window()

with open("config.json", "r") as file:
    config = json.load(file)

db_name = config["db_name"]
# SQLite bazaga ulanish
try:
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
except Exception as xato:
    print(f"❌ SQLite ulanishda xato: {xato}")
    exit(1)

driver.get(config["otm_url"])
driver.find_element(By.NAME, "FormAdminLogin[login]").send_keys(config["login"])
driver.find_element(By.NAME, "FormAdminLogin[password]").send_keys(config["parol"])
time.sleep(10)

cursor.execute("SELECT MAX(group_id) FROM student_list")
end_group_id = str(cursor.fetchone()[0] or "0")

cursor.execute("""
    SELECT DISTINCT curriculum_id, education_year_code, semester_code, group_id, group_name
    FROM student_list
    WHERE student_status_code = 11
    ORDER BY group_id ASC
""")
guruhlar = cursor.fetchall()

def hammasini_tanlash(parent_id):
    try:
        checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f'#{parent_id} input[type="checkbox"]'))
        )
        checkbox.click()
    except Exception as xato:
        print(f"Xato: {parent_id} uchun checkbox topilmadi - {xato}")

def jami_sonni_olish(parent_id):
    try:
        time.sleep(0.5)
        summary = driver.find_element(By.CSS_SELECTOR, f'#{parent_id} span.summary').text
        son = int(re.search(r'jami (\d+)', summary).group(1))
        return son
    except Exception as xato:
        print(f"Xato: {parent_id} uchun jami son topilmadi - {xato}")
        return 0

def talabalarni_ochirish(curriculum, education_year_code, semester_code, group_id):
    try:
        cursor.execute("""
            DELETE FROM student_list
            WHERE curriculum_id = ?
            AND education_year_code = ?
            AND semester_code = ?
            AND group_id = ?
        """, (curriculum, education_year_code, semester_code, group_id))
        conn.commit()
        print(f"❌ {group_id} guruhdan {cursor.rowcount} talaba o‘chirildi")
    except Exception as xato:
        print(f"‼️ Xato: {group_id} talabalarini o‘chirishda xato - {xato}")

for guruh in guruhlar:
    try:
        curriculum_id, education_year_code, semester_code, group_id, group_name = map(str, guruh)
        time.sleep(3)

        driver.get(config['otm_url'])
        driver.refresh()

        url = (
            f"{config['otm_url']}curriculum/student-register?"
            f"EStudentMeta%5B_curriculum%5D={curriculum_id}&"
            f"EStudentMeta%5B_education_year%5D={education_year_code}&"
            f"EStudentMeta%5B_semestr%5D={semester_code}&"
            f"EStudentMeta%5B_group%5D={group_id}&"
            f"_pjax=%23admin-grid"
        )
        print(f"{group_id} / {end_group_id} guruh sahifasi ochilmoqda...")
        driver.get(url)
        time.sleep(0.5)

        hammasini_tanlash('data-grid-subject-subject')
        ochirilgan_fanlar_soni = jami_sonni_olish('data-grid-subject-subject')


#################### fanlarga birikkanlarni o`chiradi ####################

        # driver.find_element(By.ID, "delete").click()   
        # time.sleep(0.5)
        # Alert(driver).accept()

        # print(f"🔴 {group_id} - {group_name}: {ochirilgan_fanlar_soni} fan o‘chirildi")
        # time.sleep(1)

#################### fanlarga birikkanlarni o`chiradi ####################



        hammasini_tanlash('data-grid')
        hammasini_tanlash('data-grid-subject')

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "assign"))
        ).click()

        jami_fanlar = jami_sonni_olish('data-grid-subject')
        driver.refresh()

        for fanlar in range(1, jami_fanlar + 1):
            fan_turi = driver.find_element(By.XPATH, f"/html/body/div/div[2]/section[2]/div/div[1]/div[2]/div/div/div[2]/div[1]/table/tbody/tr[{fanlar}]/td[3]")
            if fan_turi.text == "Tanlov":
                hammasini_tanlash('data-grid')
                fan_nomi = driver.find_element(By.XPATH, f"/html/body/div/div[2]/section[2]/div/div[1]/div[2]/div/div/div[2]/div[1]/table/tbody/tr[{fanlar}]/td[2]")
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"/html/body/div/div[2]/section[2]/div/div[1]/div[2]/div/div/div[2]/div[1]/table/tbody/tr[{fanlar}]/td[1]/input"))
                ).click()
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "assign"))
                ).click()
                print(f"🔵 {group_id} - {group_name}: {fan_nomi.text} fani biriktirildi")
                time.sleep(1)

        jami_talabalar = jami_sonni_olish('data-grid')
        biriktirilgan_fanlar = jami_sonni_olish('data-grid-subject-subject')
        print(f"🟢 {group_id} - {group_name}: {jami_talabalar} talaba {jami_fanlar} fanga biriktirildi")
        print(f"✅ {group_id} - {group_name}: Jami {biriktirilgan_fanlar} fan biriktirildi\n")
    except Exception as xato:
        print(f"Xato {group_id} guruhda: {xato}")
        continue

conn.close()
print("Barcha guruhlar fanga biriktirildi va talabalar o‘chirildi!")
driver.quit()
sys.stdout.fayl.close()
sys.stdout = sys.stdout.konsol
