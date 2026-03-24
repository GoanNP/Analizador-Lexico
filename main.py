from lexer import parseExpressao

def main():
    with open("teste1.txt") as f:
        linhas = f.readlines()

    for linha in linhas:        #le todas as linhas no arquivo e chama a expressao parseExpressao para cada uma
        try:
            tokens = parseExpressao(linha)
            print(tokens)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()