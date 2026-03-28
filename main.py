import sys
from lexer import parseExpressao
from assembly import gerarAssembly
from executor import executarExpressao, exibirResultados


def main():
    nome_arquivo = sys.argv[1]

    linhas = lerArquivo(nome_arquivo)

    memoria = {}
    historico = []

    open("assembly.txt", "w").close()

    for linha in linhas:
        try:
            linha_strip = linha.strip()
            if not linha_strip:
                continue

            tokens = parseExpressao(linha)

            resultado = executarExpressao(tokens, memoria, historico)

            asm = gerarAssembly(tokens)

            exibirResultados(
                linha,
                tokens,
                resultado,
                asm,
                memoria,
                historico,
                "assembly.txt"
            )

        except Exception as e:
            print(f"Erro na linha '{linha.strip()}': {e}")


def lerArquivo(nome):
    with open(nome, "r") as f:
        return f.readlines()


if __name__ == "__main__":
    main()