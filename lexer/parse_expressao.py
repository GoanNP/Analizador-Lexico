from lexer.estados import estadoInicial


def parseExpressao(linha):
    tokens = []
    i = 0
    estado = estadoInicial
    linha = linha.strip()

    while i < len(linha):
        i, token, estado = estado(linha, i)
        if token is not None:
            tokens.append(token)

    return tokens
