from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from src.config import TIMEOUT_PADRAO, PLANILHA_LOCAL, criar_opcoes_chrome, configurar_download
from src.downloader import baixar_planilha
from src.reader import carregar_dados
from src.formulario import preencher_formulario
from src.resultado import capturar_resultado, exibir_resultado
from src.atualizador_planilha import atualizar_planilha


def main() -> None:
    driver = webdriver.Chrome(options=criar_opcoes_chrome())
    configurar_download(driver)
    wait = WebDriverWait(driver, TIMEOUT_PADRAO)
    try:
        baixar_planilha(driver, wait)
    finally:
        driver.quit()

    df = carregar_dados(PLANILHA_LOCAL)
    resultados_por_email = {}

    # uma sessao de navegador por solicitante: o Windows so garante o foco de
    # janela necessario para o PyAutoGUI de forma confiavel logo apos a
    # janela ser criada (ver src/formulario.py)
    for _, linha in df.iterrows():
        dados_solicitante = linha.to_dict()
        email = dados_solicitante["Email do Solicitante"]

        driver = webdriver.Chrome(options=criar_opcoes_chrome())
        wait = WebDriverWait(driver, TIMEOUT_PADRAO)
        try:
            preencher_formulario(driver, wait, dados_solicitante)
            resultado = capturar_resultado(driver, wait, email)
            exibir_resultado(email, resultado)
            resultados_por_email[email] = resultado
        finally:
            driver.quit()

    atualizar_planilha(PLANILHA_LOCAL, resultados_por_email)


if __name__ == "__main__":
    main()
