from assembly import ehNumero

def parseExpressao(linha):      #enquanto tiver caracteres não verificados na linha,     
    tokens = []                 #esssa função vai chamar a função estado inicial para verificar cada um individualmente
    i = 0
    estado = estadoInicial

    while i < len(linha):
        i, token, estado = estado(linha, i)
        if token:
            tokens.append(token)

    for j in range(len(tokens) - 1):
        if ehNumero(tokens[j]) and float(tokens[j]) < 0:
            if tokens[j + 1] == "^":
                raise Exception("Erro: potência com base negativa não permitida")

    return tokens


def tokens_sem_parenteses(tokens):
    return [t for t in tokens if t not in "()"]


def estadoInicial(linha, i):    #le os caracteres um por vez, se for um numero chama a função estadoNumero e uma letra o estadoIndentificador
    c = linha[i]                #se for um caracter valido retorna ele e aumenta o contador i

    if c.isspace():
        return i + 1, None, estadoInicial

    if c in "()":
        return i + 1, c, estadoInicial

    if c.isdigit():
        return i, None, estadoNumero

    if c.isalpha():
        return i, None, estadoIdentificador

    if c == '-' and i + 1 < len(linha) and linha[i + 1].isdigit():
        return i, None, estadoNumero

    if c in "+-*/%^":
        if c == '/' and i + 1 < len(linha) and linha[i + 1] == '/':
            return i + 2, "//", estadoInicial
        return i + 1, c, estadoInicial

    raise Exception(f"Token invalido: ", c)


def estadoNumero(linha, i):
    num = ""
    pontos = 0

    if linha[i] == '-':
        num += '-'
        i += 1

    while i < len(linha):
        c = linha[i]

        if c.isdigit():
            num += c
        elif c == '.':
            if pontos == 1:
                raise Exception(f"Numero invalido: ", num)
            pontos += 1
            num += c
        else:
            break
        i += 1

    return i, num, estadoInicial


def estadoIdentificador(linha, i):  #verificar se o comando é valido e retorna ele e aumenta o contador
    ident = ""

    while i < len(linha) and linha[i].isalpha():
        ident += linha[i]
        i += 1

    if ident not in ["RES", "MEM"]:
        raise Exception(f"Identificador invalido: ", ident)

    return i, ident, estadoInicial