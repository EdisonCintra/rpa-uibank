import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.config import DRIVE_FOLDER_URL, NOME_ARQUIVO_PLANILHA

EXPORT_URL = "https://drive.google.com/uc?export=download&id={file_id}"


def baixar_planilha(driver, wait: WebDriverWait) -> None:
    driver.get(DRIVE_FOLDER_URL)

    # o Drive gera classes CSS ofuscadas que mudam entre versões (ex.: "NYP1ee",
    # "i92Sbe") — o atributo data-tooltip com o nome do arquivo é o seletor
    # estável disponível na UI atual
    seletor = f"[data-tooltip^='{NOME_ARQUIVO_PLANILHA}']"
    arquivo = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, seletor)))
    file_id = arquivo.get_attribute("data-id")

    # navega direto para a URL de export do Drive em vez de clicar em botão ou
    # usar atalho de teclado — a sessão já está autenticada, então isso baixa o
    # arquivo sem depender de seletores/atalhos instáveis da UI do Drive
    driver.get(EXPORT_URL.format(file_id=file_id))

    time.sleep(2)  # aguarda o download concluir no diretório configurado
