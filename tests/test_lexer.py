import pytest
from lexer.parse_expressao import parseExpressao


# ---------------------------------------------------------------------------
# Entradas válidas
# ---------------------------------------------------------------------------

def test_expressao_inteiros_simples():
    assert parseExpressao("3 2 +") == ["3", "2", "+"]


def test_numero_real():
    assert parseExpressao("3.14 2.0 +") == ["3.14", "2.0", "+"]


def test_todos_operadores():
    resultado = parseExpressao("5 3 - 2 * 4 / 9 % 2 ^ 1 +")
    assert resultado == ["5", "3", "-", "2", "*", "4", "/", "9", "%", "2", "^", "1", "+"]


def test_parenteses_simples():
    assert parseExpressao("(3 2 +)") == ["(", "3", "2", "+", ")"]


def test_parenteses_aninhados():
    assert parseExpressao("(51 (25 56 +) *)") == [
        "(", "51", "(", "25", "56", "+", ")", "*", ")"
    ]


def test_comando_res():
    assert parseExpressao("5 RES") == ["5", "RES"]


def test_comando_mem_armazenar():
    assert parseExpressao("3.14 MEM") == ["3.14", "MEM"]


def test_comando_mem_recuperar():
    assert parseExpressao("MEM 2 +") == ["MEM", "2", "+"]


def test_espacos_multiplos():
    assert parseExpressao("3   2   +") == ["3", "2", "+"]


def test_linha_com_newline():
    # readlines() inclui '\n' no final — deve ser ignorado
    assert parseExpressao("10 20 +\n") == ["10", "20", "+"]


def test_expressao_so_numero():
    assert parseExpressao("42") == ["42"]


def test_numero_zero():
    assert parseExpressao("0 0 +") == ["0", "0", "+"]


# ---------------------------------------------------------------------------
# Entradas inválidas
# ---------------------------------------------------------------------------

def test_numero_malformado_dois_pontos():
    with pytest.raises(ValueError, match="malformado"):
        parseExpressao("3.14.5 2 +")


def test_numero_termina_com_ponto():
    with pytest.raises(ValueError, match="malformado"):
        parseExpressao("3. 2 +")


def test_identificador_invalido():
    with pytest.raises(ValueError, match="inválido"):
        parseExpressao("ABC 2 +")


def test_identificador_invalido_minusculo():
    with pytest.raises(ValueError, match="inválido"):
        parseExpressao("res 2 +")


def test_caractere_invalido_arroba():
    with pytest.raises(ValueError, match="inválido"):
        parseExpressao("3 @ 2")


def test_caractere_invalido_hash():
    with pytest.raises(ValueError, match="inválido"):
        parseExpressao("3 # 2")
