import json
import re
from time import sleep

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

global RESULT, TMP_RESULT_OBJ, TMP_RESULT_LIST, PRODUCT_NAME, SHOPPING_URL

RESULT = []
TMP_RESULT_OBJ = {}
TMP_RESULT_LIST = []
PRODUCT_NAME = ""
SHOPPING_URL = ""


def read_input_file() -> list:
    """
    Lê os dados de entrada.
    :return: retorna uma lista com dados lidos
    """
    excel_data_df = pd.read_excel('entrada.xlsx')
    return excel_data_df['Produtos'].tolist()


def format_input_string(input_list: list) -> list:
    """
    Limpa os dados de entrada.
    :param input_list: lista com dados de entrada.
    :return: nova lista com dados de entrada tratados.
    """
    new_list = []
    for input_data in input_list:
        input_data = str(input_data).rstrip()
        new_list.append(input_data)
    return new_list


class Selenium:
    """
    Classe contém método único apenas para roubar 'cookies' e o html usando selenium
    """

    def __init__(self) -> None:
        self.op = webdriver.ChromeOptions()
        # self.op.add_argument("headless")
        self.op.add_argument("--no-sandbox")
        self.op.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=self.op)

    def process(self) -> None:
        """
        Inicia as requisições.
        :return: None.
        """
        #  Url base do scrapper
        url = "https://www.google.com"
        self.driver.get(url)
        self.delay()

        page_element = self.driver.find_element(
            by="xpath", value="/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input")
        page_element.click()
        page_element.send_keys("Ar Condicionado Split Hw On/off Eco Garden Gree 18000 Btus, Quente/Frio, 220V, "
                               "Monofásico – GWH18QD-D3NNB4B")
        page_element.submit()
        self.delay()

        page_element = self.driver.find_element(by="xpath", value='//*[@id="hdtb-msb"]/div[1]/div/div[2]/a')
        page_element.click()
        self.delay()

        #  Pegando HTML da página
        write_html(html=self.driver.page_source, prefix_name="analise")

        shopping_link_list = self.verify_if_compare(html=self.driver.page_source)
        if shopping_link_list is None:
            print("Não encontrei link do shopping comparação")
            raise Exception("Erro!")

        for index in range(len(shopping_link_list)):
            # TMP_RESULT_LIST.clear()
            # TMP_RESULT_OBJ.clear()

            shopping_url = url + shopping_link_list[index]
            print("shopping url -->", shopping_url)

            self.driver.get(shopping_url)

            #  Ordena usando o filtro do google
            page_element = self.driver.find_element(by="xpath", value='//*[@id="sh-osd__headers"]/th[4]/a')
            page_element.click()

            write_html(html=self.driver.page_source, prefix_name="tabela")

            print(f"tabela --> {index}")
            product_name = get_product_name(html=self.driver.page_source)
            print("product name -->", PRODUCT_NAME)
            product_table = scrapper_table(html=self.driver.page_source,
                                           product_name=product_name, shopping_url=shopping_url)

        RESULT.append(TMP_RESULT_LIST)
        print("Fora")
        print()
        print(RESULT)
        with open("final_result.json", "w") as f:
            f.write(json.dumps(RESULT))
        sleep(999)
        # #  Coletando ‘cookies’ do selenium
        # cookie = self.driver.get_cookies()

    @staticmethod
    def delay():
        sleep(.3)

    @staticmethod
    def verify_if_compare(html: str) -> list | None:
        """
        Verifica se dentro do html contem o link para comparar preços.
        :param html: para ser analisado.
        :return:
        """
        soup = BeautifulSoup(html, "html.parser")
        shopping_link = soup.find_all("a", attrs={"class": "iXEZD"})
        if shopping_link:
            link_list = format_link_string(link_list=shopping_link)
            return link_list
        else:
            return None


def get_product_name(html: str) -> str:
    """
    :rtype: object
    :param html: html da página
    :return: nome do produto situado no html
    """
    soup = BeautifulSoup(html, "html.parser")
    a_tag = soup.find_all("a")
    for i in range(len(a_tag)):
        if i == 7:
            # print(a_tag[i])
            # print("ok")
            product_name = str(a_tag[i]).split(">")
            product_name = product_name[-2].replace("</a", "").rstrip()
            print("nome do produto --->", product_name)
            return product_name


def format_link_string(link_list: list) -> list:
    """
    Verifica se possui o link de comparação com 10 ou mais lojas.
    :param link_list: uma lista com todas as ofertas de comparação.
    :return: lista de todos os links possíveis com 10 ou mais lojas
    """
    new_link_list = []
    for link in link_list:
        link = str(link)
        if "Comparar preços de <span>10 ou mais</span> lojas</a>" in link:
            link = str(link).replace(">Comparar preços de <span>10 ou mais</span> lojas</a>", "")
            link = str(link).replace('<a class="iXEZD" data-sh-gr="line" href="', "")
            new_link_list.append(link)
    return new_link_list


def scrapper_table(html: str, product_name: str, shopping_url: str) -> list:
    """
    :param shopping_url:
    :param product_name:
    :param html: pagina shopping ja ordenada do menor para o maior
    :return: uma lista com objetos representando cada linha dentro do shopping
    """

    soup = BeautifulSoup(html, "html.parser")
    table_data = soup.find_all("table")

    products_values = []
    for i in range(len(table_data)):
        for j in range(len(table_data[i])):
            j = table_data[j].find_all_next("tr")
            for k in range(len(j)):
                products_values = get_all_td(html_slice=str(j[k]), product_name=product_name, shopping_url=shopping_url)
    return products_values


def get_all_td(html_slice: str, product_name: str, shopping_url: str) -> list:
    """
    :param shopping_url:
    :param product_name:
    :param html_slice: uma fatia da tabela
    :return: valores dentro de uma lista (valor, valor parcelado)
    """
    product_list = []
    soup = BeautifulSoup(html_slice, "html.parser")
    td = soup.find_all("td")
    for i in range(len(td)):
        if i == 2:
            # print(td[i])
            product_values = extract_values(txt=str(td[i]), product_name=product_name, shopping_url=shopping_url)
            print("get_all_td", product_values)
            product_list.append(product_values)
    return product_list


def extract_values(txt: str, product_name: str, shopping_url: str) -> list[str, str] | None:
    """
    :param shopping_url:
    :param product_name:
    :param txt: parte de uma tag <td> html
    :return: uma lista contento na pos 0 o valor e na pos 1 o valor parcelado se houver, caso nao None
    """
    # print(type(txt))
    # print(txt)
    temp_obj = {}
    original = txt.split(">")
    value = original[2].replace("</span", "").replace("R$", "")

    installment = ""

    try:
        installment = original[4].replace(" - com juros</div", "").replace("R$", "")
    except Exception as ex:
        print("Não encontrei com juros", ex)

    try:
        installment = original[4].replace(" - sem juros</div", "").replace("R$", "")
    except Exception as ex:
        print("Não encontrei sem juros", ex)

    # print(txt)
    # TMP_RESULT_OBJ.clear()

    validation = re.search(r'^\s*(?:[1-9]\d{0,2}(?:\.\d{3})*|0),\d{2}$', value)
    if validation:
        value = validation.group().rstrip().replace(" ", "")
        installment = str(installment).rstrip().replace(" ", "")

        print("product name -->", PRODUCT_NAME)
        print("shopping url -->", SHOPPING_URL)

        temp_obj["tabela_referencia"] = shopping_url
        temp_obj["nome_produto"] = product_name
        temp_obj["preco_produto"] = value
        temp_obj["preco_parcelado"] = installment

        # print("OBJT -->", temp_obj)
        # print("LISTA -->", TMP_RESULT_LIST)

        TMP_RESULT_LIST.append(temp_obj)
        print()
        print()
        # print("DEPOIS -->", TMP_RESULT_LIST)

        return [value, installment]
    else:
        print("Não encontrei valor e nem valor de parcelamento!")
    return


def write_html(html: str, prefix_name: str) -> None:
    """
    :param html: string html.
    :param prefix_name: nome do arquivo.
    :return: None
    """
    with open(f"{prefix_name}.html", "w") as file:
        file.write(html)
    return


def main() -> None:
    """
    Main.
    :return: None
    """
    products = read_input_file()
    products = format_input_string(products)
    for i in products:
        print(i)

    Selenium().process()


if __name__ == "__main__":
    main()
