from assembly import ehNumero


def _inteiro_truncado(x):
    return int(float(x))


def _div_quociente_trunc_zero(a, b):
    q = abs(a) // abs(b)
    if (a < 0) ^ (b < 0):
        q = -q
    return q


def executarExpressao(tokens, memoria, historico): 
    pilha = []
    ultimo_gravado_mem = None

    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token == "(" or token == ")":
            i += 1
            continue

        if ehNumero(token):
            pilha.append(float(_inteiro_truncado(token)))

        elif token == "MEM":
            if pilha:
                v = float(_inteiro_truncado(pilha.pop()))
                memoria["MEM"] = v
                ultimo_gravado_mem = v
            else:
                if "MEM" not in memoria:
                    raise Exception("Erro: MEM nao possui valor armazenado")
                pilha.append(float(_inteiro_truncado(memoria["MEM"])))

        elif token == "RES":
            if not pilha:
                raise Exception("Erro: RES requer um indice N na pilha")
            n = int(_inteiro_truncado(pilha.pop()))
            if n < 1 or n > len(historico):
                raise Exception(
                    f"Erro: RES({n}) invalido, historico tem {len(historico)} entradas"
                )
            pilha.append(float(historico[-n]))

        elif token in ["+", "-", "*", "/", "//", "%", "^"]:
            if len(pilha) < 2:
                raise Exception(f"Erro: operacao '{token}' requer dois operandos")

            b = _inteiro_truncado(pilha.pop())
            a = _inteiro_truncado(pilha.pop())

            if token == "+":
                resultado = float(a + b)
            elif token == "-":
                resultado = float(a - b)
            elif token == "*":
                resultado = float(a * b)
            elif token == "/" or token == "//":
                if b == 0:
                    raise Exception("Erro: divisao por zero")
                resultado = float(_div_quociente_trunc_zero(a, b))
            elif token == "%":
                if b == 0:
                    raise Exception("Erro: resto por zero")
                q = _div_quociente_trunc_zero(a, b)
                resultado = float(a - q * b)
            elif token == "^":
                if a < 0:
                    raise Exception("Erro: potencia com base negativa")
                resultado = float(a ** b if b >= 0 else 1)

            pilha.append(resultado)

        i += 1

    if pilha:
        resultado_final = pilha[-1]
    elif ultimo_gravado_mem is not None:
        resultado_final = float(ultimo_gravado_mem)
    else:
        raise Exception("Erro: expressao invalida")

    historico.append(resultado_final)
    memoria["_LAST"] = resultado_final

    return resultado_final


def exibirResultados(linha, tokens, resultado, asm, memoria=None, historico=None, arquivo_saida=None):
    saida = []
    
    saida.append(f"Linha:     {linha.strip()}")
    saida.append(f"Tokens:    {tokens}")
    saida.append(f"Resultado: {resultado}")

    if memoria is not None:
        saida.append(f"Memoria:   {memoria}")
    if historico is not None:
        saida.append(f"Historico: {historico}")

    texto_terminal = "\n".join(saida)
    print(texto_terminal)

    saida.append("Assembly:")
    saida.append(asm)
    saida.append("-" * 50)

    texto_final = "\n".join(saida)


    if arquivo_saida:
        with open(arquivo_saida, "a") as f:
            f.write(texto_final + "\n")
