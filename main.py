from lexer.parse_expressao import parseExpressao


def main():
    with open("teste1.txt") as f:
        linhas = f.readlines()

    for i, linha in enumerate(linhas, start=1):
        try:
            tokens = parseExpressao(linha)
            print(f"Linha {i}: {tokens}")
        except ValueError as e:
            print(f"Linha {i}: Erro léxico — {e}")


if __name__ == "__main__":
    main()
