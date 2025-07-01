from openpyxl import load_workbook

excel_nomi = 'selenium/aylanma_varaqa/talaba_aylanma.xlsx'
# Excel faylini o'qing
wb = load_workbook(excel_nomi)

# Yangi list oching, agar mavjud bo'lmasa
if 'Statistika' not in wb.sheetnames:
    wb.create_sheet(title='Statistika-tasdiqlanmagan')
sheet = wb['Statistika']

# Sarlavhalarni yozing
sheet['A1'] = 'Fakultet'
sheet['B1'] = 'Jami talaba'
sheet['C1'] = 'Registrator ofisi'
sheet['D1'] = 'Dekan'
sheet['E1'] = 'Marketing'
sheet['F1'] = 'Buxgalteriya'
sheet['G1'] = 'Kutubxona'
sheet['H1'] = 'Yotoqxona'

# Har bir fakultetdagi talabalar sonini va tasdiqlanmaganlarni hisoblash
fakultetlar = {}
tasdiqlanmagan = {
    'Registrator ofisi': {}, 'Dekan': {}, 'Marketing': {}, 'Buxgalteriya': {},
    'Kutubxona': {}, 'Yotoqxona': {}
}
for row in wb['Talabalar'].iter_rows(min_row=2, values_only=True):
    fakultet = row[6]  # G ustunida fakultet nomi
    rol = row[4]  # E ustunida rol
    ikonka = row[5]  # F ustunida ikonka (badge)
    if fakultet:
        # Fakultet bo'yicha umumiy talaba sonini hisoblash
        fakultetlar[fakultet] = fakultetlar.get(fakultet, 0) + 1
        if ikonka != "badge bg-green" and rol:
            for key in tasdiqlanmagan.keys():
                if key in rol:
                    tasdiqlanmagan[key][fakultet] = tasdiqlanmagan[key].get(fakultet, 0) + 1

# Ma'lumotlarni Excelga yozing
row_num = 2
for fakultet, soni in fakultetlar.items():
    sheet[f'A{row_num}'] = fakultet
    sheet[f'B{row_num}'] = (fakultetlar[fakultet])/ 6  # G ustunidagi son
    sheet[f'C{row_num}'] = tasdiqlanmagan['Registrator ofisi'].get(fakultet, 0)
    sheet[f'D{row_num}'] = tasdiqlanmagan['Dekan'].get(fakultet, 0)
    sheet[f'E{row_num}'] = tasdiqlanmagan['Marketing'].get(fakultet, 0)
    sheet[f'F{row_num}'] = tasdiqlanmagan['Buxgalteriya'].get(fakultet, 0)
    sheet[f'G{row_num}'] = tasdiqlanmagan['Kutubxona'].get(fakultet, 0)
    sheet[f'H{row_num}'] = tasdiqlanmagan['Yotoqxona'].get(fakultet, 0)
    row_num += 1

# Jami qatorini qo'shing
sheet[f'A{row_num}'] = 'Jami'
# Har bir ustun uchun umumiy sonni hisoblash
sheet[f'B{row_num}'] = (sum(fakultetlar.values()))/6  # Umumiy talaba soni
sheet[f'C{row_num}'] = sum(tasdiqlanmagan['Registrator ofisi'].values())
sheet[f'D{row_num}'] = sum(tasdiqlanmagan['Dekan'].values())
sheet[f'E{row_num}'] = sum(tasdiqlanmagan['Marketing'].values())
sheet[f'F{row_num}'] = sum(tasdiqlanmagan['Buxgalteriya'].values())
sheet[f'G{row_num}'] = sum(tasdiqlanmagan['Kutubxona'].values())
sheet[f'H{row_num}'] = sum(tasdiqlanmagan['Yotoqxona'].values())

# Faylni saqlang
wb.save(excel_nomi)