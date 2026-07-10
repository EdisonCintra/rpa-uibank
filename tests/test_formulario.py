from unittest.mock import MagicMock, patch

import pytest

from src.formulario import preencher_campo_texto, ativar_janela_navegador, TENTATIVAS_DIGITACAO


@patch("src.formulario.pyautogui")
@patch("src.formulario.gw")
def test_ativar_janela_navegador_ativa_janela_encontrada(mock_gw, mock_pyautogui):
    driver = MagicMock(title="UiBank")
    janela = MagicMock()
    mock_gw.getWindowsWithTitle.return_value = [janela]

    ativar_janela_navegador(driver)

    janela.activate.assert_called_once()


@patch("src.formulario.time.sleep", return_value=None)
@patch("src.formulario.pyautogui")
@patch("src.formulario.gw")
def test_preencher_campo_texto_confirma_valor_digitado(mock_gw, mock_pyautogui, mock_sleep):
    mock_gw.getWindowsWithTitle.return_value = []
    driver = MagicMock(title="UiBank")
    wait = MagicMock()
    campo = MagicMock()
    campo.get_attribute.return_value = "maria@teste.com"
    wait.until.return_value = campo

    preencher_campo_texto(driver, wait, ("id", "email"), "maria@teste.com")

    campo.click.assert_called_once()
    campo.clear.assert_called_once()
    mock_pyautogui.write.assert_called_once_with("maria@teste.com", interval=0.05)


@patch("src.formulario.time.sleep", return_value=None)
@patch("src.formulario.pyautogui")
@patch("src.formulario.gw")
def test_preencher_campo_texto_levanta_erro_apos_tentativas_esgotadas(
    mock_gw, mock_pyautogui, mock_sleep
):
    mock_gw.getWindowsWithTitle.return_value = []
    driver = MagicMock(title="UiBank")
    wait = MagicMock()
    campo = MagicMock()
    campo.get_attribute.return_value = ""  # nunca bate com o valor esperado
    wait.until.return_value = campo

    with pytest.raises(RuntimeError, match="Nao foi possivel preencher"):
        preencher_campo_texto(driver, wait, ("id", "email"), "maria@teste.com")

    assert mock_pyautogui.write.call_count == TENTATIVAS_DIGITACAO
