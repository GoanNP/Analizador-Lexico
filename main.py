def main():

    with open("teste1.txt") as f:
        linhas = f.readlines()

    for linha in linhas:
        res = parseExpressao(linha)

        print(res)

def parseExpressao(linha):
    tokens = []
    i = 0
    estado = estadoInicial

    while i < len(linha):
        i, token, estado = estado(linha, i)
        if token:
            tokens.append(token)

    return tokens


def estadoInicial(linha, i):
    c = linha[i]

    if c.isspace():
        return i+1, None, estadoInicial

    if c == '(' or c == ')':
        return i+1, c, estadoInicial

    if c.isdigit():
        return i, None, estadoNumero

    if c.isalpha():
        return i, None, estadoIdentificador

    if c in "+-*/%^":
        return i+1, c, estadoInicial


def estadoNumero(linha, i):
    num = ""

    while i < len(linha):
        c = linha[i]

        if c.isdigit():
            num += c
        elif c == '.':
            num += c
        else:
            break
        i += 1

    return i, num, estadoInicial


def estadoIdentificador(linha, i):
    ident = ""

    while i < len(linha) and linha[i].isalpha():
        ident += linha[i]
        i += 1

    return i, ident, estadoInicial

if __name__ == "__main__":
    main()