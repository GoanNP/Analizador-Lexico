from lexer import parseExpressao, tokens_sem_parenteses
from assembly import gerarAssembly
from executor import executarExpressao, exibirResultados


def main():
    linhas = lerArquivo("teste1.txt")

    memoria = {}
    historico = []

    for linha in linhas:
        try:
            linha_strip = linha.strip()
            if not linha_strip:
                continue
            tokens = parseExpressao(linha)
            print(tokens)
            asm = gerarAssembly(tokens)
            print(asm)
        except Exception as e:
            print(f"Erro: {e}")

def lerArquivo(nome):
    with open(nome) as f:
        linhas = f.readlines()
        return linhas


if __name__ == "__main__":
    main()