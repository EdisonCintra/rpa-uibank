import pandas as pd

from src.atualizador_planilha import atualizar_planilha
from src.resultado import StatusResultado


def _criar_planilha(tmp_path) -> str:
    caminho = tmp_path / "planilha.xlsx"
    pd.DataFrame(
        {
            "Email do Solicitante": ["maria@teste.com", "sandra@teste.com"],
            "Montante do Empréstimo": [10000, 120000],
            "Termo do Empréstimo": [5, 10],
            "Renda Anual Atual( Antes dos Impostos)": [30000, 40000],
            "Idade": [20, 70],
            "Status do Empréstimo": [None, None],
            "ID do Empréstimo": [None, None],
            "APR": [None, None],
        }
    ).to_excel(caminho, index=False)
    return str(caminho)


def test_atualizar_planilha_grava_aprovado_e_negado(tmp_path):
    caminho = _criar_planilha(tmp_path)
    resultados = {
        "maria@teste.com": {"status": StatusResultado.APROVADO, "id": "abc123", "apr": "8"},
        "sandra@teste.com": {
            "status": StatusResultado.NEGADO,
            "motivo": "Emprestimo acima do limite",
        },
    }

    atualizar_planilha(caminho, resultados)

    df = pd.read_excel(caminho)
    maria = df[df["Email do Solicitante"] == "maria@teste.com"].iloc[0]
    sandra = df[df["Email do Solicitante"] == "sandra@teste.com"].iloc[0]

    assert maria["Status do Empréstimo"] == "Aprovado"
    assert maria["ID do Empréstimo"] == "abc123"
    assert float(maria["APR"]) == 8.0  # openpyxl grava "8", Excel/pandas relê como numero

    assert sandra["Status do Empréstimo"] == "Negado"
    assert pd.isna(sandra["ID do Empréstimo"])
    assert pd.isna(sandra["APR"])


def test_atualizar_planilha_ignora_email_sem_resultado(tmp_path):
    caminho = _criar_planilha(tmp_path)

    resultados = {"maria@teste.com": {"status": StatusResultado.APROVADO, "id": "x", "apr": "1"}}
    atualizar_planilha(caminho, resultados)

    df = pd.read_excel(caminho)
    sandra = df[df["Email do Solicitante"] == "sandra@teste.com"].iloc[0]
    assert pd.isna(sandra["Status do Empréstimo"])
