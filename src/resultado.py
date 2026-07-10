import time
from enum import Enum

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from src.config import PASTA_SCREENSHOTS

# pyautogui exige um display grafico real -- no CI (Linux sem display) a
# importacao falha. Ver o mesmo padrao/motivo em formulario.py.
try:
    import pyautogui
except Exception:
    pyautogui = None

LARGURA_EMAIL = 25
LARGURA_STATUS = 10


class StatusResultado(str, Enum):
    APROVADO = "Aprovado"
    NEGADO = "Negado"
    INDEFINIDO = "Indefinido"


def _registrar_evidencia(status: StatusResultado, email: str) -> None:
    """PyAutoGUI captura a tela como evidência auditável de cada desfecho.
    O nome do arquivo inclui o solicitante — sem isso, a única forma de saber
    de quem é a evidência seria abrir a imagem uma por uma."""
    identificador = email.split("@")[0]
    nome_arquivo = f"{identificador}_{status.value.lower()}_{int(time.time())}.png"
    pyautogui.screenshot(f"{PASTA_SCREENSHOTS}/{nome_arquivo}")


def capturar_resultado(driver, wait, email: str) -> dict:
    try:
        wait.until(EC.presence_of_element_located((By.ID, "loanID")))
        resultado = {
            "status": StatusResultado.APROVADO,
            "id": driver.find_element(By.ID, "loanID").text.strip(),
            "apr": driver.find_element(By.ID, "rateValue").text.strip(),
        }
        _registrar_evidencia(resultado["status"], email)
        return resultado
    except TimeoutException:
        pass

    try:
        motivo = driver.find_element(By.ID, "failMessage").text.strip()
        resultado = {"status": StatusResultado.NEGADO, "motivo": motivo}
        _registrar_evidencia(resultado["status"], email)
        return resultado
    except NoSuchElementException:
        resultado = {"status": StatusResultado.INDEFINIDO, "motivo": "Resultado nao identificado"}
        _registrar_evidencia(resultado["status"], email)
        return resultado


def exibir_resultado(email: str, resultado: dict) -> None:
    status = resultado["status"]
    email_fmt = email.ljust(LARGURA_EMAIL)
    status_fmt = status.value.ljust(LARGURA_STATUS)

    if status == StatusResultado.APROVADO:
        print(f"[OK] {email_fmt} | {status_fmt} | ID: {resultado['id']} | APR: {resultado['apr']}%")
    elif status == StatusResultado.NEGADO:
        print(f"[X]  {email_fmt} | {status_fmt} | Motivo: {resultado['motivo']}")
    else:
        print(f"[?]  {email_fmt} | {status_fmt} | {resultado.get('motivo', '')}")
