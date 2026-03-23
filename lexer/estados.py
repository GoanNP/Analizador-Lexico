COMANDOS_VALIDOS = {"RES", "MEM"}
OPERADORES_VALIDOS = set("+-*/%^")


def estadoInicial(linha, i):
    c = linha[i]

    if c.isspace():
        return i + 1, None, estadoInicial

    if c in "()":
        return i, None, estadoParenteses

    if c.isdigit():
        return i, None, estadoNumero

    if c.isalpha():
        return i, None, estadoIdentificador

    if c in OPERADORES_VALIDOS:
        return i, None, estadoOperador

    raise ValueError(f"Caractere inválido '{c}' na posição {i}")


def estadoNumero(linha, i):
    num = ""
    tem_ponto = False

    while i < len(linha):
        c = linha[i]

        if c.isdigit():
            num += c
            i += 1

        elif c == ".":
            if tem_ponto:
                raise ValueError(
                    f"Número malformado '{num + c}' na posição {i}: múltiplos pontos decimais"
                )
            tem_ponto = True
            num += c
            i += 1

        else:
            break

    if num.endswith("."):
        raise ValueError(
            f"Número malformado '{num}' na posição {i}: termina com ponto decimal"
        )

    return i, num, estadoInicial


def estadoIdentificador(linha, i):
    ident = ""
    inicio = i

    while i < len(linha) and linha[i].isalpha():
        ident += linha[i]
        i += 1

    if ident not in COMANDOS_VALIDOS:
        raise ValueError(
            f"Identificador inválido '{ident}' na posição {inicio}: esperado RES ou MEM"
        )

    return i, ident, estadoInicial


def estadoOperador(linha, i):
    c = linha[i]
    return i + 1, c, estadoInicial


def estadoParenteses(linha, i):
    c = linha[i]
    return i + 1, c, estadoInicial
