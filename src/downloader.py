import time

from selenium.webdriver.support.ui import WebDriverWait

from src.config import DRIVE_FOLDER_URL, NOME_ARQUIVO_PLANILHA

EXPORT_URL = "https://drive.google.com/uc?export=download&id={file_id}"


def baixar_planilha(driver, wait: WebDriverWait) -> None:
    driver.get(DRIVE_FOLDER_URL)

    # o Drive gera classes CSS ofuscadas que mudam entre versões (ex.: "NYP1ee",
    # "i92Sbe") — o atributo data-tooltip com o nome do arquivo é o seletor
    # estável disponível na UI atual. Lemos o data-id via execute_script dentro
    # do wait para evitar StaleElementReferenceException: o Drive re-renderiza
    # a lista enquanto carrega, então guardar o WebElement e ler o atributo
    # depois pode cair em elemento obsoleto.
    seletor = f"[data-tooltip^='{NOME_ARQUIVO_PLANILHA}']"
    file_id = wait.until(
        lambda d: d.execute_script(
            "const el = document.querySelector(arguments[0]);"
            "return el ? el.getAttribute('data-id') : null;",
            seletor,
        )
    )

    # navega direto para a URL de export do Drive em vez de clicar em botão ou
    # usar atalho de teclado — a sessão já está autenticada, então isso baixa o
    # arquivo sem depender de seletores/atalhos instáveis da UI do Drive
    driver.get(EXPORT_URL.format(file_id=file_id))

    time.sleep(2)  # aguarda o download concluir no diretório configurado
