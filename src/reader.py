import pandas as pd

COLUNAS_OBRIGATORIAS = [
    "Email do Solicitante",
    "Montante do Empréstimo",
    "Termo do Empréstimo",
    "Renda Anual Atual( Antes dos Impostos)",
    "Idade",
]


def carregar_dados(caminho: str) -> pd.DataFrame:
    df = pd.read_excel(caminho)
    _validar(df)
    return df


def _validar(df: pd.DataFrame) -> None:
    for coluna in COLUNAS_OBRIGATORIAS:
        assert coluna in df.columns, f"Coluna obrigatoria ausente: {coluna}"
        assert df[coluna].notna().all(), f"Valor vazio encontrado em: {coluna}"

    assert (df["Idade"] >= 18).all(), "Solicitante menor de 18 anos encontrado"
    assert df["Email do Solicitante"].str.contains("@").all(), "Email invalido encontrado"
