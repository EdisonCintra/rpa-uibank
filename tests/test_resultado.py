from unittest.mock import MagicMock, patch

from selenium.common.exceptions import TimeoutException, NoSuchElementException

from src.resultado import capturar_resultado, exibir_resultado, StatusResultado


@patch("src.resultado.pyautogui")
def test_capturar_resultado_aprovado(mock_pyautogui):
    driver = MagicMock()
    wait = MagicMock()
    wait.until.return_value = True  # elemento #loanID encontrado

    def find_element(by, valor):
        elemento = MagicMock()
        elemento.text = "6a4fcc090f79076a36ac35c6" if valor == "loanID" else "8"
        return elemento

    driver.find_element.side_effect = find_element

    resultado = capturar_resultado(driver, wait, "maria@teste.com")

    assert resultado["status"] == StatusResultado.APROVADO
    assert resultado["id"] == "6a4fcc090f79076a36ac35c6"
    assert resultado["apr"] == "8"
    mock_pyautogui.screenshot.assert_called_once()


@patch("src.resultado.pyautogui")
def test_capturar_resultado_negado(mock_pyautogui):
    driver = MagicMock()
    wait = MagicMock()
    wait.until.side_effect = TimeoutException()  # #loanID nao apareceu

    elemento_motivo = MagicMock()
    elemento_motivo.text = "You must be at least 18 years old and the loan must not exceed 100k."
    driver.find_element.return_value = elemento_motivo

    resultado = capturar_resultado(driver, wait, "sandra@teste.com")

    assert resultado["status"] == StatusResultado.NEGADO
    assert "18 years old" in resultado["motivo"]


@patch("src.resultado.pyautogui")
def test_capturar_resultado_indefinido(mock_pyautogui):
    driver = MagicMock()
    wait = MagicMock()
    wait.until.side_effect = TimeoutException()
    driver.find_element.side_effect = NoSuchElementException()

    resultado = capturar_resultado(driver, wait, "teste@teste.com")

    assert resultado["status"] == StatusResultado.INDEFINIDO


def test_exibir_resultado_aprovado(capsys):
    exibir_resultado(
        "maria@teste.com",
        {"status": StatusResultado.APROVADO, "id": "abc123", "apr": "8"},
    )

    saida = capsys.readouterr().out
    assert "[OK]" in saida
    assert "maria@teste.com" in saida
    assert "abc123" in saida
    assert "8%" in saida


def test_exibir_resultado_negado(capsys):
    exibir_resultado(
        "sandra@teste.com",
        {"status": StatusResultado.NEGADO, "motivo": "Emprestimo acima do limite"},
    )

    saida = capsys.readouterr().out
    assert "[X]" in saida
    assert "Emprestimo acima do limite" in saida
