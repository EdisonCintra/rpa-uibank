import pandas as pd
import pytest

from src.reader import carregar_dados


def _dados_validos(**overrides):
    base = {
        "Email do Solicitante": ["maria@teste.com", "pedro@teste.com"],
        "Montante do Empréstimo": [10000, 30000],
        "Termo do Empréstimo": [5, 10],
        "Renda Anual Atual( Antes dos Impostos)": [30000, 50000],
        "Idade": [20, 30],
    }
    base.update(overrides)
    return base


def _criar_planilha(tmp_path, dados: dict) -> str:
    caminho = tmp_path / "planilha.xlsx"
    pd.DataFrame(dados).to_excel(caminho, index=False)
    return str(caminho)


def test_carrega_planilha_valida(tmp_path):
    caminho = _criar_planilha(tmp_path, _dados_validos())

    df = carregar_dados(caminho)

    assert len(df) == 2
    assert df["Email do Solicitante"].tolist() == ["maria@teste.com", "pedro@teste.com"]


def test_falha_quando_coluna_obrigatoria_ausente(tmp_path):
    dados = _dados_validos()
    del dados["Idade"]
    caminho = _criar_planilha(tmp_path, dados)

    with pytest.raises(AssertionError, match="Coluna obrigatoria ausente"):
        carregar_dados(caminho)


def test_falha_quando_campo_obrigatorio_vazio(tmp_path):
    caminho = _criar_planilha(tmp_path, _dados_validos(Idade=[20, None]))

    with pytest.raises(AssertionError, match="Valor vazio encontrado"):
        carregar_dados(caminho)


def test_falha_quando_idade_menor_que_18(tmp_path):
    caminho = _criar_planilha(tmp_path, _dados_validos(Idade=[17, 30]))

    with pytest.raises(AssertionError, match="menor de 18"):
        carregar_dados(caminho)


def test_falha_quando_email_invalido(tmp_path):
    emails_invalidos = ["maria-sem-arroba.com", "pedro@teste.com"]
    dados = _dados_validos(**{"Email do Solicitante": emails_invalidos})
    caminho = _criar_planilha(tmp_path, dados)

    with pytest.raises(AssertionError, match="Email invalido"):
        carregar_dados(caminho)
