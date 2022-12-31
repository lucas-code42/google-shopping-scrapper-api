#!/usr/bin/env python3.10

import smtplib
import traceback
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(to_addr: str, email_token: str) -> bool:
    """
    :param email_token: Token password
    :param to_addr: Email destinatário.
    :return: bool, caso processo ocorrra bem, retorna True do contrário False
    """
    print("\n\nINICIANDO SERVIÇO DE EMAIL", flush=True)
    try:
        msg = MIMEMultipart()
        from_addr = "lucasdearaujo.brandao@gmail.com"

        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = "Serviço Relatório de Produtos API"
        body = "Serviço Relatório de Produtos API"

        msg.attach(MIMEText(body, 'plain'))
        filename = "products_report.xlsx"
        attachment = open("report.xlsx", "rb")
        p = MIMEBase('application', 'octet-stream')
        p.set_payload(attachment.read())
        encoders.encode_base64(p)

        p.add_header("Content-Disposition", f"attachment; filename= {filename}")
        msg.attach(p)
        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.login(from_addr, email_token)
        text = msg.as_string()
        s.sendmail(from_addr, to_addr, text)

        s.quit()
        print("\n\nEMAIL ENVIADO COM SUCESSO", flush=True)
        return True

    except Exception as ex:
        traceback.print_exc()
        print("Erro -->", ex)
        print("\n\nSERVIÇO DE EMAIL ERROR", flush=True)
        return False
