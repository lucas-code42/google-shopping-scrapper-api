#!/usr/bin/env python3.10

import re
import traceback
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from xlsxwriter import Workbook

global RESULT, TMP_RESULT_LIST

RESULT = []
TMP_RESULT_LIST = []


class Selenium:
    """
    Classe contém método único apenas para roubar 'cookies' e o html usando selenium
    """

    def __init__(self) -> None:
        self.op = webdriver.ChromeOptions()
        self.op.add_argument("headless")
        self.op.add_argument("--no-sandbox")
        self.op.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=self.op)

    def process(self, product_to_search: str) -> bool:
        """        Inicia as requisições.
        :return: None.
        """
        try:

            print("\n\nINICIANDO PROCESSAMENTO", flush=True)

            url = "https://www.google.com"
            self.driver.get(url)
            self.delay()

            page_element = self.driver.find_element(
                by="xpath", value="/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input")
            page_element.click()
            page_element.send_keys(product_to_search)
            page_element.submit()
            self.delay()

            page_element = self.driver.find_element(by="xpath", value='//*[@id="hdtb-msb"]/div[1]/div/div[2]/a')
            page_element.click()
            self.delay()

            #  Pegando HTML da página
            shopping_link_list = self.verify_if_compare(html=self.driver.page_source)
            if shopping_link_list is None:
                print("Não encontrei link do shopping comparação")
                raise Exception()

            for index in range(len(shopping_link_list)):
                shopping_url = url + shopping_link_list[index]

                self.driver.get(shopping_url)

                #  Ordena usando o filtro do google
                page_element = self.driver.find_element(by="xpath", value='//*[@id="sh-osd__headers"]/th[4]/a')
                page_element.click()

                product_name = get_product_name(html=self.driver.page_source)
                scrapper_table(html=self.driver.page_source,
                               product_name=product_name,
                               shopping_url=shopping_url)

            RESULT.append(TMP_RESULT_LIST)

            if not generate_report(data=RESULT):
                raise Exception()

            print("\n\nFim do processamento.", flush=True)
            return True

        except Exception as ex:
            traceback.print_exc()
            print("Erro -->", ex)
            print("\n\nErro de processamento.", flush=True)
            return False

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
            product_name = str(a_tag[i]).split(">")
            product_name = product_name[-2].replace("</a", "").rstrip()
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
    market_place_sellers = []
    for i in range(len(table_data)):
        market_place = soup.find_all("a", attrs={"target": "_blank"})
        for index in range(len(market_place)):
            if market_place[index].text == "Acessar o siteAbre em uma nova janela":
                continue
            elif market_place[index].text == "Learn more":
                continue
            else:
                seller = str(market_place[index].text)
                seller = seller.replace("Abre em uma nova janela", "").rstrip()
                market_place_sellers.append(seller)

        for j in range(len(table_data[i])):
            j = table_data[j].find_all_next("tr")
            for k in range(len(j)):
                products_values = get_all_td(html_slice=str(j[k]),
                                             product_name=product_name,
                                             shopping_url=shopping_url)
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
    marketplace = ""
    txt = ""
    for i in range(len(td)):
        if i == 11:
            marketplace = td[i]
            marketplace = str(marketplace).split("url?q=")[1]
            marketplace = marketplace.split(".com")[0].replace("https://www.", "")
        if i == 2:
            txt = td[i]
        if marketplace != "" and txt != "":
            product_values = extract_values(txt=str(txt),
                                            product_name=product_name,
                                            shopping_url=shopping_url,
                                            market_place_sellers=marketplace)
    return product_list


def extract_values(txt: str, product_name: str, shopping_url: str, market_place_sellers: str) -> list[str, str] | None:
    """
    :param market_place_sellers:
    :param shopping_url:
    :param product_name:
    :param txt: parte de uma tag <td> html
    :return: uma lista contento na pos 0 o valor e na pos 1 o valor parcelado se houver, caso nao None
    """
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

    validation = re.search(r'^\s*(?:[1-9]\d{0,2}(?:\.\d{3})*|0),\d{2}$', value)
    if validation:
        value = validation.group().rstrip().replace(" ", "")
        installment = str(installment).rstrip().replace(" ", "")

        temp_obj["marketplace"] = market_place_sellers
        temp_obj["tabela_referencia"] = shopping_url
        temp_obj["nome_produto"] = product_name
        temp_obj["preco_produto"] = value
        temp_obj["preco_parcelado"] = installment

        print(flush=True)
        print("Dados coletados:", flush=True)
        print("Marketplace:", market_place_sellers, flush=True)
        print("Tabela:", shopping_url, flush=True)
        print("Nome do Produto:", product_name, flush=True)
        print("Preço do Produto:", product_name, flush=True)
        print("Preço a Prazo:", installment, flush=True)
        print(flush=True)

        TMP_RESULT_LIST.append(temp_obj)
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


def generate_report(data: list) -> bool:
    print("\n\n GERANDO RELATÓRIO")
    try:
        ordered_list = [
            "marketplace",
            "tabela_referencia",
            "nome_produto",
            "preco_produto",
            "preco_parcelado"
        ]

        wb = Workbook("report.xlsx")
        ws = wb.add_worksheet("rascunho")

        first_row = 0
        for header in ordered_list:
            col = ordered_list.index(header)
            ws.write(first_row, col, header)

        row = 1
        for player in data:
            for obj in player:
                for _key, _value in obj.items():
                    col = ordered_list.index(_key)
                    ws.write(row, col, _value)
                row += 1  # enter the next row
        wb.close()
        print("\n\nRELATÓRIO GERADO COM SUCESSO")
        return True

    except Exception as ex:
        traceback.print_exc()
        print("Erro -->", ex)
        print("\n\nERRO AO GERAR RELATÓRIO")
        return False
