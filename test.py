# import re
#
#
# txt = '<td class="SH30Lb"><span class="g9WBQb fObmGc">R$1.691,10</span><div class="E5ziJ">10 x R$187,' \
#       '90 - com juros</div></td>'
#
# original = txt.split(">")
# print(original)
# txt = original[2].replace("</span", "").replace("R$", "")
# txt2 = original[4].replace(" - com juros</div", "").replace("R$", "")
# # txt2 = original[4].replace(" - sem juros</div", "").replace("R$", "") pode ser sem juros
# print(txt2)
#
# x = re.search(r'^\s*(?:[1-9]\d{0,2}(?:\.\d{3})*|0),\d{2}$', txt)
#
# if x:
#     value = str(x.group())
#     print("aqui", value)
#     print("YES! We have a match!")
# else:
#     print("No match")
#
#
# x = re.search(r'[0-9]{2} x ^\s*(?:[1-9]\d{0,2}(?:\.\d{3})*|0),\d{2}$', txt2)
#
# if x:
#     value = str(x.group())
#     print("aqui", value)
#     print("YES! We have a match!")
# else:
#     print("No match")


# import pandas as pd
#
# student = [{"Name": "Vishvajit Rao", "age": 23, "Occupation": "Developer", "Language": "Python"},
#            {"Name": "Lucas", "age": 25, "Occupation": "Dev", "Language": "java"}
#            ]
#
# # convert into dataframe
# for i in student:
#     df = pd.DataFrame(data=i, index=[1])
#
# # convert into excel
# df.to_excel("students.xlsx", index=False)
# print("Dictionary converted into excel...")


from xlsxwriter import Workbook


def generate_report(data: list):
    ordered_list = [
        "marketplace",
        "tabela_referencia",
        "nome_produto", "preco_produto",
        "preco_parcelado"
    ]

    wb = Workbook("relatorio.xlsx")
    ws = wb.add_worksheet("rascunho")  # Or leave it blank. The default name is "Sheet 1"

    first_row = 0
    for header in ordered_list:
        col = ordered_list.index(header)  # We are keeping order.
        ws.write(first_row, col, header)  # We have written first row which is the header of worksheet also.

    row = 1
    for player in data:
        for _key, _value in player.items():
            col = ordered_list.index(_key)
            ws.write(row, col, _value)
        row += 1  # enter the next row
    wb.close()


if __name__ == "__main__":
