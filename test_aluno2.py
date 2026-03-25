import unittest

from lexer import parseExpressao, tokens_sem_parenteses
from assembly import gerarAssembly
from executor import executarExpressao


class TestAFD(unittest.TestCase):
    def test_numero_decimal_soma(self):
        t = parseExpressao("3.14 2.0 +")
        self.assertEqual(t, ["3.14", "2.0", "+"])

    def test_parenteses_ignorados_lexico(self):
        t = parseExpressao("( 3.14 2.0 + )")
        self.assertEqual(t, ["(", "3.14", "2.0", "+", ")"])

    def test_res_token(self):
        t = parseExpressao("5 RES")
        self.assertEqual(t, ["5", "RES"])

    def test_numero_invalido_dois_pontos(self):
        with self.assertRaises(Exception):
            parseExpressao("3.14.5 2.0 +")


class TestExecutor(unittest.TestCase):
    def test_rpn_alinhado_ao_assembly_int_literal(self):
        m, h = {}, []
        r = executarExpressao(parseExpressao("3.14 2.0 +"), m, h)
        self.assertAlmostEqual(r, 5.0)
        self.assertEqual(m["_LAST"], r)

    def test_mem_write_e_read(self):
        m, h = {}, []
        executarExpressao(parseExpressao("42 MEM"), m, h)
        self.assertAlmostEqual(m["MEM"], 42.0)
        self.assertAlmostEqual(
            executarExpressao(parseExpressao("MEM"), m, h), 42.0
        )

    def test_res_com_historico(self):
        m, h = {}, []
        executarExpressao(parseExpressao("10 20 +"), m, h)
        executarExpressao(parseExpressao("5 5 +"), m, h)
        r = executarExpressao(parseExpressao("2 RES"), m, h)
        self.assertAlmostEqual(r, 30.0)

    def test_divisao_e_resto(self):
        m, h = {}, []
        self.assertAlmostEqual(
            executarExpressao(parseExpressao("7 3 //"), m, h), 2.0
        )
        m, h = {}, []
        self.assertAlmostEqual(
            executarExpressao(parseExpressao("7 3 %"), m, h), 1.0
        )

    def test_expressao_com_parenteses_no_executor(self):
        m, h = {}, []
        r = executarExpressao(parseExpressao("( 10 3 + )"), m, h)
        self.assertAlmostEqual(r, 13.0)

    def test_res_indice_invalido(self):
        m, h = {}, []
        executarExpressao(parseExpressao("1 1 +"), m, h)
        with self.assertRaises(Exception):
            executarExpressao(parseExpressao("5 RES"), m, h)


class TestAssembly(unittest.TestCase):
    def test_parenteses_filtrados_antes_do_gerador(self):
        toks = parseExpressao("( 3.14 2.0 + )")
        asm = gerarAssembly(tokens_sem_parenteses(toks))
        self.assertIn("MOV", asm)
        self.assertIn("ADD", asm)
        self.assertNotIn("(", asm.split("_start:")[-1])

    def test_literal_truncado_como_no_gerador(self):
        asm = gerarAssembly(tokens_sem_parenteses(parseExpressao("3.14 0 +")))
        self.assertIn("#3", asm)

    def test_mem_apenas_load_no_gerador(self):
        asm = gerarAssembly(tokens_sem_parenteses(parseExpressao("7 MEM")))
        self.assertIn("MEM", asm)
        self.assertIn("LDR", asm)

    def test_resultado_em_res_word(self):
        asm = gerarAssembly(tokens_sem_parenteses(parseExpressao("2 3 +")))
        self.assertIn("STR", asm)
        self.assertIn("RES", asm)


if __name__ == "__main__":
    unittest.main()
