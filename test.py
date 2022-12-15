import re


txt = '<td class="SH30Lb"><span class="g9WBQb fObmGc">R$1.691,10</span><div class="E5ziJ">10 x R$187,' \
      '90 - com juros</div></td>'

original = txt.split(">")
print(original)
txt = original[2].replace("</span", "").replace("R$", "")
txt2 = original[4].replace(" - com juros</div", "").replace("R$", "")
# txt2 = original[4].replace(" - sem juros</div", "").replace("R$", "") pode ser sem juros
print(txt2)

x = re.search(r'^\s*(?:[1-9]\d{0,2}(?:\.\d{3})*|0),\d{2}$', txt)

if x:
    value = str(x.group())
    print("aqui", value)
    print("YES! We have a match!")
else:
    print("No match")


x = re.search(r'[0-9]{2} x ^\s*(?:[1-9]\d{0,2}(?:\.\d{3})*|0),\d{2}$', txt2)

if x:
    value = str(x.group())
    print("aqui", value)
    print("YES! We have a match!")
else:
    print("No match")
