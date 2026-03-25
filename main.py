from lexer import parseExpressao
from assembly import gerarAssembly

def main():
    linhas = lerArquivo("teste1.txt")

    for linha in linhas:        #le todas as linhas no arquivo e chama a expressao parseExpressao para cada uma
        try:
            tokens = parseExpressao(linha)
            print(tokens)
            asm = gerarAssembly(tokens)
            print(asm)
        except Exception as e:
            print(e)

def lerArquivo(nome):
    with open(nome) as f:
        linhas = f.readlines()
        return linhas


if __name__ == "__main__":
    main()