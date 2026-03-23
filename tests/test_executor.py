import pytest
from lexer.parse_expressao import parseExpressao
from executor.executar_expressao import executarExpressao, validar_parenteses


def executar(expressao, memoria=None, historico=None):
    """Helper: cria contexto e executa uma expressão."""
    if memoria is None:
        memoria = {}
    if historico is None:
        historico = []
    tokens = parseExpressao(expressao)
    resultado = executarExpressao(tokens, memoria, historico)
    return resultado, memoria, historico


# ---------------------------------------------------------------------------
# Operações básicas
# ---------------------------------------------------------------------------

def test_adicao():
    resultado, _, _ = executar("3 2 +")
    assert resultado == 5.0


def test_subtracao():
    resultado, _, _ = executar("5 3 -")
    assert resultado == 2.0


def test_multiplicacao():
    resultado, _, _ = executar("3 4 *")
    assert resultado == 12.0


def test_divisao_float():
    resultado, _, _ = executar("10 4 /")
    assert resultado == 2.5


def test_resto():
    resultado, _, _ = executar("10 3 %")
    assert resultado == 1.0


def test_potencia():
    resultado, _, _ = executar("2 8 ^")
    assert resultado == 256.0


def test_numero_real():
    resultado, _, _ = executar("3.14 2.0 +")
    assert abs(resultado - 5.14) < 1e-9


def test_precisao_64bits():
    # IEEE 754 double: 1/3 deve ter precisão de 64 bits
    resultado, _, _ = executar("1 3 /")
    assert abs(resultado - (1 / 3)) < 1e-15


# ---------------------------------------------------------------------------
# Expressões com parênteses aninhados
# ---------------------------------------------------------------------------

def test_parenteses_simples():
    resultado, _, _ = executar("(3 2 +)")
    assert resultado == 5.0


def test_parenteses_aninhados():
    # (51 (25 56 +) *) → 51 * 81 = 4131
    resultado, _, _ = executar("(51 (25 56 +) *)")
    assert resultado == 4131.0


def test_parenteses_duplo_aninhado():
    # ((1.5 2.0 *) (3.0 4.0 *) /) → 3.0 / 12.0 = 0.25
    resultado, _, _ = executar("((1.5 2.0 *) (3.0 4.0 *) /)")
    assert abs(resultado - 0.25) < 1e-9


# ---------------------------------------------------------------------------
# Comando MEM
# ---------------------------------------------------------------------------

def test_mem_armazenar():
    _, memoria, _ = executar("3.14 MEM")
    assert memoria["MEM"] == 3.14


def test_mem_recuperar():
    memoria = {"MEM": 3.14}
    resultado, _, _ = executar("MEM 1 +", memoria=memoria)
    assert abs(resultado - 4.14) < 1e-9


def test_mem_armazenar_e_recuperar_sequencial():
    memoria = {}
    historico = []
    tokens = parseExpressao("5.0 MEM")
    executarExpressao(tokens, memoria, historico)
    tokens = parseExpressao("MEM 2 *")
    resultado = executarExpressao(tokens, memoria, historico)
    assert resultado == 10.0


def test_mem_sobrescrever():
    memoria = {}
    historico = []
    tokens = parseExpressao("10 MEM")
    executarExpressao(tokens, memoria, historico)
    tokens = parseExpressao("99 MEM")
    executarExpressao(tokens, memoria, historico)
    assert memoria["MEM"] == 99.0


def test_mem_nao_inicializada():
    with pytest.raises(ValueError, match="não inicializada"):
        tokens = parseExpressao("MEM 1 +")
        executarExpressao(tokens, {}, [])


# ---------------------------------------------------------------------------
# Comando RES
# ---------------------------------------------------------------------------

def test_res_ultimo_resultado():
    memoria = {}
    historico = []
    tokens = parseExpressao("10 5 +")
    executarExpressao(tokens, memoria, historico)   # historico = [15.0]
    tokens = parseExpressao("1 RES")
    resultado = executarExpressao(tokens, memoria, historico)
    assert resultado == 15.0


def test_res_segundo_resultado():
    memoria = {}
    historico = []
    tokens = parseExpressao("10 5 +")
    executarExpressao(tokens, memoria, historico)   # historico = [15.0]
    tokens = parseExpressao("3 3 *")
    executarExpressao(tokens, memoria, historico)   # historico = [15.0, 9.0]
    tokens = parseExpressao("2 RES")
    resultado = executarExpressao(tokens, memoria, historico)
    assert resultado == 15.0


def test_res_em_expressao():
    memoria = {}
    historico = []
    tokens = parseExpressao("4 4 *")
    executarExpressao(tokens, memoria, historico)   # historico = [16.0]
    tokens = parseExpressao("1 RES 2 +")
    resultado = executarExpressao(tokens, memoria, historico)
    assert resultado == 18.0


def test_res_indice_invalido():
    with pytest.raises(ValueError, match="inválido"):
        tokens = parseExpressao("5 RES")
        executarExpressao(tokens, {}, [])


def test_res_historico_vazio():
    with pytest.raises(ValueError, match="inválido"):
        tokens = parseExpressao("1 RES")
        executarExpressao(tokens, {}, [])


# ---------------------------------------------------------------------------
# Erros
# ---------------------------------------------------------------------------

def test_divisao_por_zero():
    with pytest.raises(ValueError, match="zero"):
        executar("5 0 /")


def test_resto_por_zero():
    with pytest.raises(ValueError, match="zero"):
        executar("5 0 %")


def test_operandos_insuficientes():
    with pytest.raises(ValueError, match="operandos"):
        executar("3 +")


def test_parenteses_faltando_fecha():
    with pytest.raises(ValueError):
        tokens = parseExpressao("(3 2 +")
        executarExpressao(tokens, {}, [])


def test_parenteses_faltando_abre():
    with pytest.raises(ValueError):
        tokens = ["3", "2", "+", ")"]
        executarExpressao(tokens, {}, [])


def test_validar_parenteses_balanceados():
    validar_parenteses(["(", "3", "2", "+", ")"])  # não lança


def test_validar_parenteses_desbalanceados():
    with pytest.raises(ValueError):
        validar_parenteses(["(", "3", "2", "+"])
