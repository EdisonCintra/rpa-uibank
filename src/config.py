import os

from selenium.webdriver.chrome.options import Options

FORM_URL = "https://uibank.uipath.com/loans/apply"
DRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/1I1byidvRDJk4T_Sfl7QmdZjPEnfHLQi5"
DRIVE_FOLDER_ID = "1I1byidvRDJk4T_Sfl7QmdZjPEnfHLQi5"

TIMEOUT_PADRAO = 10
PASTA_SCREENSHOTS = "screenshots"
PASTA_DADOS = "dados"
NOME_ARQUIVO_PLANILHA = "PedidosEmprestimo.xlsx"
PLANILHA_LOCAL = os.path.join(PASTA_DADOS, NOME_ARQUIVO_PLANILHA)


def criar_opcoes_chrome() -> Options:
    """Configura o Chrome para baixar arquivos direto em PASTA_DADOS, sem
    diálogo de confirmação — mantém o download dentro do projeto em vez da
    pasta padrão do usuário."""
    opcoes = Options()
    pasta_absoluta = os.path.abspath(PASTA_DADOS)
    opcoes.add_experimental_option(
        "prefs",
        {
            "download.default_directory": pasta_absoluta,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        },
    )
    return opcoes


def configurar_download(driver) -> None:
    """As prefs do Chrome sozinhas não são confiáveis para automação — o
    Chrome atual só respeita o diretório de download quando isso também é
    confirmado via CDP (Page.setDownloadBehavior)."""
    pasta_absoluta = os.path.abspath(PASTA_DADOS)
    driver.execute_cdp_cmd(
        "Page.setDownloadBehavior",
        {"behavior": "allow", "downloadPath": pasta_absoluta},
    )
