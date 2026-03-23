OPERADORES = set("+-*/%^")


def _aplicar_operador(op, a, b):
    """Aplica um operador binário com precisão de 64 bits (IEEE 754)."""
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        if b == 0.0:
            raise ValueError("Divisão por zero")
        return a / b
    if op == "%":
        if b == 0.0:
            raise ValueError("Resto por zero")
        return float(int(a) % int(b))
    if op == "^":
        return a ** b
    raise ValueError(f"Operador desconhecido '{op}'")


def validar_parenteses(tokens):
    """
    Valida se os parênteses nos tokens estão balanceados.
    Lança ValueError caso contrário.
    """
    profundidade = 0
    for token in tokens:
        if token == "(":
            profundidade += 1
        elif token == ")":
            profundidade -= 1
            if profundidade < 0:
                raise ValueError("Parêntese ')' sem correspondente '('")
    if profundidade != 0:
        raise ValueError("Parêntese '(' sem correspondente ')'")


def executarExpressao(tokens, memoria, historico):
    """
    Avalia uma expressão RPN a partir dos tokens gerados pelo parseExpressao.

    Parâmetros:
        tokens   : lista de tokens (strings) vinda do parseExpressao
        memoria  : dict compartilhado entre chamadas — armazena variáveis (ex.: MEM)
        historico: lista compartilhada de resultados anteriores (usada por RES)

    Retorno:
        resultado (float) da expressão avaliada

    Operadores suportados: + - * / % ^
    Comandos especiais:
        V MEM  — armazena V na memória (chave 'MEM')
        MEM    — empilha o valor armazenado em MEM
        N RES  — empilha o N-ésimo resultado anterior (1 = mais recente)
    """
    validar_parenteses(tokens)

    pilha = []

    for token in tokens:

        # Parênteses são ignorados na avaliação RPN — a pilha lida naturalmente
        if token in ("(", ")"):
            continue

        elif token == "MEM":
            if pilha:
                # (V MEM) → armazena o topo da pilha em memória, mantém o valor
                memoria["MEM"] = pilha[-1]
            else:
                # (MEM) → empilha o valor armazenado
                if "MEM" not in memoria:
                    raise ValueError("MEM: memória não inicializada")
                pilha.append(memoria["MEM"])

        elif token == "RES":
            if not pilha:
                raise ValueError("RES: índice ausente na pilha")
            n = pilha.pop()
            if n != int(n):
                raise ValueError(f"RES: índice deve ser inteiro, recebido {n}")
            n = int(n)
            if n < 1 or n > len(historico):
                raise ValueError(
                    f"RES: índice {n} inválido — histórico tem {len(historico)} entradas"
                )
            pilha.append(historico[-n])

        elif token in OPERADORES:
            if len(pilha) < 2:
                raise ValueError(
                    f"Operador '{token}' requer 2 operandos, pilha tem {len(pilha)}"
                )
            b = pilha.pop()
            a = pilha.pop()
            pilha.append(_aplicar_operador(token, a, b))

        else:
            try:
                pilha.append(float(token))
            except ValueError:
                raise ValueError(f"Token inesperado '{token}'")

    if len(pilha) != 1:
        raise ValueError(
            f"Expressão inválida: {len(pilha)} valor(es) na pilha ao final (esperado 1)"
        )

    resultado = pilha[0]
    historico.append(resultado)
    return resultado
