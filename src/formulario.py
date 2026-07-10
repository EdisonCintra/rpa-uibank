import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
import pygetwindow as gw

from src.config import FORM_URL

TENTATIVAS_DIGITACAO = 5


def ativar_janela_navegador(driver) -> None:
    """PyAutoGUI só digita na janela com foco do sistema operacional — o clique
    do Selenium só garante foco dentro da página (DOM). Sem isso, o Chrome
    pode estar aberto atrás de outra janela e a digitação vai para o lugar
    errado (ou para lugar nenhum). O Windows nem sempre concede essa troca de
    foco de forma confiável (varia por timing), por isso essa chamada é
    repetida a cada tentativa em preencher_campo_texto()."""
    janelas = gw.getWindowsWithTitle(driver.title)
    if janelas:
        try:
            janelas[0].activate()
        except gw.PyGetWindowException:
            # falso-positivo conhecido do pygetwindow no Windows: a API do
            # SO retorna sucesso (GetLastError=0), mas a biblioteca levanta
            # excecao mesmo assim
            pass
        time.sleep(0.6)


def preencher_campo_texto(driver, wait: WebDriverWait, seletor: tuple, valor) -> None:
    """Selenium localiza e foca o campo; PyAutoGUI digita como um usuário real.

    O foco de janela do Windows para processos automatizados é intermitente
    (ver ativar_janela_navegador), então digitar pode falhar silenciosamente.
    Por isso o valor é conferido depois de cada tentativa — falha rápido e
    clara em vez de submeter o formulário com dado incompleto."""
    valor_str = str(valor)
    for _ in range(TENTATIVAS_DIGITACAO):
        ativar_janela_navegador(driver)
        campo = wait.until(EC.element_to_be_clickable(seletor))
        campo.click()
        campo.clear()
        pyautogui.write(valor_str, interval=0.05)
        time.sleep(0.2)
        if campo.get_attribute("value") == valor_str:
            return

    raise RuntimeError(
        f"Nao foi possivel preencher o campo {seletor} com '{valor_str}' "
        f"apos {TENTATIVAS_DIGITACAO} tentativas (falha de foco do PyAutoGUI)"
    )


def preencher_formulario(driver, wait: WebDriverWait, dados_solicitante: dict) -> None:
    driver.get(FORM_URL)
    wait.until(EC.presence_of_element_located((By.ID, "email")))
    time.sleep(0.5)  # da tempo da animacao de maximizar a janela terminar

    preencher_campo_texto(driver, wait, (By.ID, "email"), dados_solicitante["Email do Solicitante"])
    preencher_campo_texto(
        driver, wait, (By.ID, "amount"), dados_solicitante["Montante do Empréstimo"]
    )

    # campo nativo <select> — usa o suporte do Selenium em vez de PyAutoGUI,
    # já que os valores das opções (1/3/5/10) são fixos e conhecidos
    termo = wait.until(EC.element_to_be_clickable((By.ID, "term")))
    Select(termo).select_by_value(str(int(dados_solicitante["Termo do Empréstimo"])))

    preencher_campo_texto(
        driver, wait, (By.ID, "income"), dados_solicitante["Renda Anual Atual( Antes dos Impostos)"]
    )
    preencher_campo_texto(driver, wait, (By.ID, "age"), dados_solicitante["Idade"])

    _submeter(driver, wait)


def _submeter(driver, wait: WebDriverWait) -> None:
    """O Angular processa a validacao reativa do ultimo campo digitado de
    forma assincrona — clicar no Submit imediatamente apos preencher pode
    acontecer antes do formulario ser marcado como valido. Por isso confere
    se a URL mudou e clica de novo se o Angular ainda nao tiver reagido."""
    for _ in range(TENTATIVAS_DIGITACAO):
        time.sleep(0.3)
        driver.find_element(By.ID, "submitButton").click()
        try:
            wait.until(lambda d: d.current_url != FORM_URL)
            return
        except TimeoutException:
            continue

    raise RuntimeError("Nao foi possivel submeter o formulario apos varias tentativas")
