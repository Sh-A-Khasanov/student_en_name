###############################################################
#   uquv_yili ga tegishli bo`lgan talabalarning
#   uquv_yili_uchun yildaki GPA sini hisoblaydi
###############################################################

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import re
import math


uquv_yili = 2024  # Talaba filtrlari shu yildaki talabalarni chiqaradi
uquv_yili_uchun = "2023-2024"   # filterlar tanlanganidan keyin qaysi yil ucun gpa hisoblash



# Selenium sozlamalari
options = webdriver.ChromeOptions()
options.add_argument("--log-level=3")  # Faqat muhim xatolar chiqadi
driver = webdriver.Chrome(options=options)
driver.maximize_window()

# config.json faylini o‘qiymiz
with open("config.json", "r") as file:
    config = json.load(file)


otm_url = config["otm_url"]
driver.get(otm_url)  

# Login va parolni kiritish
login_value = config["login"]
parol_value = config["parol"]

login = driver.find_element(By.NAME, "FormAdminLogin[login]")
login.send_keys(login_value)
parol = driver.find_element(By.NAME, "FormAdminLogin[password]")
parol.send_keys(parol_value)
time.sleep(15)  # Sayt yuklanishini kutish va kirish tugmasini bosish uchun vaqt






driver.get(f"{otm_url}performance/gpa-add") 

jami_talabani_olish = driver.find_element(By.XPATH, "/html/body/div/div[2]/section[2]/div/form/div/div[1]/div/div/div[2]/span").text

# '1-50 / jami 21 286 ta'
match = re.search(r'jami\s([\d\s]+)\sta', jami_talabani_olish)
if match:
    jami_talaba = int(match.group(1).replace(" ", ""))
    print(f"jami_talaba : {jami_talaba}")  # 21286

jami_page=math.ceil(jami_talaba/50)
print(f"total_page : {jami_page}")
time.sleep(1)

 
for page in range(1,jami_page+1):
    try:
        print(page)    
        driver.get(f"{otm_url}performance/gpa-add?page={page}&per-page=50&EStudentGpaMeta%5B_education_year%5D={uquv_yili}")
        time.sleep(0.5)
        
        # qaysi uquv_yili_uchun'ni ochish
        wait = WebDriverWait(driver, 10)
        dropdown = wait.until(EC.element_to_be_clickable((By.ID, "select2-estudentgpameta-education_year-container")))
        dropdown.click()
        

        # Kerakli variantni tanlash (masalan, 2023-2024)
        option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[text()='{uquv_yili_uchun}']")))
        option.click()

        all_student=driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/section[2]/div/form/div/div[1]/div/div/div[1]/table/thead/tr/th[1]/input")
        all_student.click()
        time.sleep(1)
        Hisoblash_button=driver.find_element(By.XPATH, "/html/body/div/div[2]/section[2]/div/form/div/div[2]/div/div/div[5]/button")
        Hisoblash_button.click()
        time.sleep(1)
        Alert(driver).accept()
        time.sleep(1)
    except Exception as e:
        print("❌ Xatolik:\n\n", e)
 

print("Barcha GPA hisoblandi!")
driver.quit()



