import xlsxwriter
workbook = xlsxwriter.Workbook('formula.xlsx')
worksheet = workbook.add_worksheet()
# данные
expenses = (
    ['Аренда', 1000],
    ['Комуналка', 100],
    ['Еда', 300],
    ['Качалка', 50],
)
for i, (item, cost) in enumerate(expenses, start=1):
    worksheet.write(f'A{i}', item)
    worksheet.write(f'B{i}', cost)
# колонкой ниже добавить подсчет суммы
worksheet.write('A5', 'Итого:')
worksheet.write('B5', '=SUM(B1:B4)')
# сохраняем и закрываем
workbook.close()
