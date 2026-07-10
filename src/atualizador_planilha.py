import openpyxl

from src.resultado import StatusResultado

COLUNA_EMAIL = "Email do Solicitante"
COLUNA_STATUS = "Status do Empréstimo"
COLUNA_ID = "ID do Empréstimo"
COLUNA_APR = "APR"


def atualizar_planilha(caminho: str, resultados: dict) -> None:
    """Escreve o resultado de cada solicitante de volta nas colunas de saida
    da propria planilha baixada (Status/ID/APR) -- elas chegam vazias do
    Drive, servem exatamente para isso."""
    workbook = openpyxl.load_workbook(caminho)
    planilha = workbook.active

    cabecalho = {celula.value: celula.column for celula in planilha[1]}
    col_email = cabecalho[COLUNA_EMAIL]
    col_status = cabecalho[COLUNA_STATUS]
    col_id = cabecalho[COLUNA_ID]
    col_apr = cabecalho[COLUNA_APR]

    for linha in planilha.iter_rows(min_row=2):
        email = linha[col_email - 1].value
        resultado = resultados.get(email)
        if resultado is None:
            continue

        linha[col_status - 1].value = resultado["status"].value
        if resultado["status"] == StatusResultado.APROVADO:
            linha[col_id - 1].value = resultado["id"]
            linha[col_apr - 1].value = resultado["apr"]

    workbook.save(caminho)
