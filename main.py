import argparse
import os

from lexer import parseExpressao
from assembly import gerarAssembly
from executor import executarExpressao, exibirResultados


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Analisador RPN: lê expressões de um arquivo e exibe os resultados."
    )
    ap.add_argument(
        "arquivo",
        nargs="?",
        default="teste1.txt",
        help="Arquivo com uma expressão por linha (default: teste1.txt)",
    )
    ap.add_argument(
        "--asm",
        action="store_true",
        help="Gera arquivo .s com o Assembly de cada expressão.",
    )
    args = ap.parse_args(argv)

    linhas = lerArquivo(args.arquivo)
    memoria = {}
    historico = []
    resultados = []
    blocos_asm = []

    for linha in linhas:
        try:
            linha_strip = linha.strip()
            if not linha_strip:
                continue

            tokens = parseExpressao(linha)
            resultado = executarExpressao(tokens, memoria, historico)
            resultados.append(resultado)

            if args.asm:
                blocos_asm.append(gerarAssembly(tokens))
        except Exception as e:
            print(f"Erro: {e}")

    if resultados:
        exibirResultados(resultados)

    if args.asm and blocos_asm:
        nome_saida = os.path.splitext(args.arquivo)[0] + ".s"
        with open(nome_saida, "w", encoding="utf-8", newline="\n") as f:
            for i, bloco in enumerate(blocos_asm, 1):
                f.write(f"// --- Expressao {i} ---\n")
                f.write(bloco + "\n\n")
        print(f"Assembly salvo em: {nome_saida}")

def lerArquivo(nome):
    with open(nome, encoding="utf-8") as f:
        linhas = f.readlines()
        return linhas


if __name__ == "__main__":
    main()