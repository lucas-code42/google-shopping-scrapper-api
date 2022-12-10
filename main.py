from time import sleep

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver


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
        page_element.send_keys("Ar Condicionado Split Hw On/off Eco Garden Gree 18000 Btus, Quente/Frio, 220V, Monofásico – GWH18QD-D3NNB4B")
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
            shopping_url = url + shopping_link_list[index]
            print(shopping_url)

            self.driver.get(shopping_url)
            page_element = self.driver.find_element(by="xpath", value='//*[@id="sh-osd__headers"]/th[4]/a')
            page_element.click()

            write_html(html=self.driver.page_source, prefix_name="tabela")

            print(f"tabela --> {index}")
            product_table = get_product_table(html=self.driver.page_source)

        print("Fora")
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


def get_product_table(html: str) -> list:
    """
    :param html: pagina shopping ja ordenada do menor para o maior
    :return: uma lista com objetos representando cada linha dentro do shopping
    """
    soup = BeautifulSoup(html, "html.parser")
    table_data = soup.find_all("table")

    print(len(table_data))

    for i in range(len(table_data)):
        for j in range(len(table_data[i])):
            j = table_data[j].find_all_next("tr")
            print("ESSA É A TR ->", j)
            print()
            print()
            print()
            print()
            for k in range(len(j)):
                print("Esse é o elemento -->", k, "-->", j[k])
                print()
                print()
                print()
                print()
        # print(i, "--->", table_data[i])
        # print()
        # print()
        # print()
    return []


def write_html(html: str, prefix_name: str) -> None:
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
