from unittest.mock import MagicMock, patch

from src.config import DRIVE_FOLDER_URL
from src.downloader import baixar_planilha, EXPORT_URL


@patch("src.downloader.time.sleep", return_value=None)
def test_baixar_planilha_localiza_arquivo_e_navega_para_url_de_export(mock_sleep):
    driver = MagicMock()
    wait = MagicMock()
    elemento = MagicMock()
    elemento.get_attribute.return_value = "abc123"
    wait.until.return_value = elemento

    baixar_planilha(driver, wait)

    wait.until.assert_called_once()
    driver.get.assert_any_call(DRIVE_FOLDER_URL)
    driver.get.assert_any_call(EXPORT_URL.format(file_id="abc123"))
    elemento.get_attribute.assert_called_once_with("data-id")
