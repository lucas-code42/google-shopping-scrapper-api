import re


txt = '<td class="SH30Lb"><span class="g9WBQb fObmGc">R$1.691,10</span><div class="E5ziJ">10 x R$187,' \
      '90 - com juros</div></td>'

txt = txt.split(">")
txt = txt[2].replace("</span", "").replace("R$", "")

x = re.search(r'^\s*(?:[1-9]\d{0,2}(?:\.\d{3})*|0),\d{2}$', txt)

if x:
    value = str(x.group())
    print("aqui", value)
    print("YES! We have a match!")
else:
    print("No match")
