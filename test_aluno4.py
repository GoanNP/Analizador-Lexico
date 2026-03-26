import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from lexer import parseExpressao
from executor import executarExpressao, exibirResultados, format_resultado_exibicao
from main import main as main_entry


class TestFormato(unittest.TestCase):
    def test_format_one_decimal(self):
        self.assertEqual(format_resultado_exibicao(5), "5.0")
        self.assertEqual(format_resultado_exibicao(3.14), "3.1")
        self.assertEqual(format_resultado_exibicao(-2), "-2.0")

    def test_exibirResultados_format(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            exibirResultados([10.0, 20.5])
        s = buf.getvalue()
        self.assertIn("[1] 10.0", s)
        self.assertIn("[2] 20.5", s)


class TestFSM_Mem(unittest.TestCase):
    def test_v_mem_e_mem(self):
        m, h = {}, []
        r1 = executarExpressao(parseExpressao("99 MEM"), m, h)
        r2 = executarExpressao(parseExpressao("MEM"), m, h)
        self.assertEqual(r1, 99.0)
        self.assertEqual(r2, 99.0)


class TestMainCLI(unittest.TestCase):
    def test_main_with_tempfile(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("99 MEM\n")
            f.write("MEM\n")
            tmp_path = f.name

        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                main_entry([tmp_path])
            s = buf.getvalue()
            self.assertIn("[1] 99.0", s)
            self.assertIn("[2] 99.0", s)
        finally:
            os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main()

