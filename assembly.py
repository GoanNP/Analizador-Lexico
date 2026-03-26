def gerarAssembly(tokens):
    text_section = []
    data_section = []
    stack = []

    reg_int = 0
    reg_double = 0
    label_count = 0
    const_count = 0
    variaveis_usadas = set()

    # ================= HELPERS =================

    def novo_reg_int():
        nonlocal reg_int
        r = f"R{reg_int}"
        reg_int += 1
        return r

    def novo_reg_double():
        nonlocal reg_double
        r = f"D{reg_double}"
        reg_double += 1
        return r

    def novo_label():
        nonlocal label_count
        l = f"L{label_count}"
        label_count += 1
        return l

    def carregar_constante(valor):
        nonlocal const_count
        const_name = f"C{const_count}"
        const_count += 1

        data_section.append(f"{const_name}: .double {float(valor)}")

        d = novo_reg_double()
        r = novo_reg_int()

        text_section.append(f"    LDR {r}, ={const_name}")
        text_section.append(f"    VLDR {d}, [{r}]")

        stack.append((d, "double"))

    # ================= OPERAÇÕES =================

    def operacao_aritmetica(op):
        (r2, _) = stack.pop()
        (r1, _) = stack.pop()

        r_dest = novo_reg_double()

        op_map = {
            "+": "VADD.F64",
            "-": "VSUB.F64",
            "*": "VMUL.F64",
            "/": "VDIV.F64"
        }

        text_section.append(f"    {op_map[op]} {r_dest}, {r1}, {r2}")
        stack.append((r_dest, "double"))

    def operacao_div_int_ou_mod(token):
        (r2, _) = stack.pop()
        (r1, _) = stack.pop()

        r1_int = novo_reg_int()
        r2_int = novo_reg_int()

        text_section.append(f"    VCVT.S32.F64 S0, {r1}")
        text_section.append(f"    VMOV {r1_int}, S0")

        text_section.append(f"    VCVT.S32.F64 S1, {r2}")
        text_section.append(f"    VMOV {r2_int}, S1")

        r_dest = novo_reg_int()
        r_temp = novo_reg_int()

        loop = novo_label()
        end = novo_label()

        text_section.append(f"    MOV {r_dest}, #0")
        text_section.append(f"    MOV {r_temp}, {r1_int}")

        text_section.append(f"{loop}:")
        text_section.append(f"    CMP {r_temp}, {r2_int}")
        text_section.append(f"    BLT {end}")
        text_section.append(f"    SUB {r_temp}, {r_temp}, {r2_int}")
        text_section.append(f"    ADD {r_dest}, {r_dest}, #1")
        text_section.append(f"    B {loop}")
        text_section.append(f"{end}:")

        if token == "%":
            stack.append((r_temp, "int"))
        else:
            stack.append((r_dest, "int"))

    def operacao_potencia():
        (r_exp, _) = stack.pop()
        (r_base, _) = stack.pop()

        r_exp_int = novo_reg_int()
        r_base_int = novo_reg_int()

        text_section.append(f"    VCVT.S32.F64 S0, {r_exp}")
        text_section.append(f"    VMOV {r_exp_int}, S0")

        text_section.append(f"    VCVT.S32.F64 S1, {r_base}")
        text_section.append(f"    VMOV {r_base_int}, S1")

        r_result = novo_reg_int()

        loop = novo_label()
        end = novo_label()

        text_section.append(f"    MOV {r_result}, #1")
        text_section.append(f"{loop}:")
        text_section.append(f"    CMP {r_exp_int}, #0")
        text_section.append(f"    BEQ {end}")
        text_section.append(f"    MUL {r_result}, {r_result}, {r_base_int}")
        text_section.append(f"    SUB {r_exp_int}, {r_exp_int}, #1")
        text_section.append(f"    B {loop}")
        text_section.append(f"{end}:")

        stack.append((r_result, "int"))

    def operacao_mem_store(valor, mem):
        carregar_constante(valor)

        (d, _) = stack.pop()

        r_addr = novo_reg_int()
        text_section.append(f"    LDR {r_addr}, ={mem}")
        text_section.append(f"    VSTR.F64 {d}, [{r_addr}]")

        variaveis_usadas.add(mem)

    def operacao_mem_load(mem):
        d = novo_reg_double()
        r = novo_reg_int()

        text_section.append(f"    LDR {r}, ={mem}")
        text_section.append(f"    VLDR {d}, [{r}]")

        stack.append((d, "double"))
        variaveis_usadas.add(mem)

    def operacao_mem_operacao(valor, mem, op):
        carregar_constante(valor)

        d2 = novo_reg_double()
        r = novo_reg_int()

        text_section.append(f"    LDR {r}, ={mem}")
        text_section.append(f"    VLDR {d2}, [{r}]")

        variaveis_usadas.add(mem)

        stack.append((d2, "double"))

        if op in ["+", "-", "*", "/"]:
            operacao_aritmetica(op)
        elif op in ["//", "%"]:
            operacao_div_int_ou_mod(op)
        elif op == "^":
            operacao_potencia()

    # ================= PARSER RECURSIVO =================

    def processar(tokens_local):
        i = 0
        while i < len(tokens_local):
            token = tokens_local[i]

            if token == "(":
                nivel = 1
                j = i + 1
                sub = []

                while nivel > 0:
                    if tokens_local[j] == "(":
                        nivel += 1
                    elif tokens_local[j] == ")":
                        nivel -= 1

                    if nivel > 0:
                        sub.append(tokens_local[j])

                    j += 1

                processar(sub)
                i = j
                continue

            elif ehNumero(token):
                carregar_constante(token)

            elif token.isalpha():
                operacao_mem_load(token)

            elif token in ["+", "-", "*", "/"]:
                operacao_aritmetica(token)

            elif token in ["//", "%"]:
                operacao_div_int_ou_mod(token)

            elif token == "^":
                operacao_potencia()

            i += 1

    # ================= INÍCIO =================

    text_section.append(".global _start")
    text_section.append(".text")
    text_section.append("_start:")

    processar(tokens)

    text_section.append("    B .")

    if data_section or variaveis_usadas:
        data_section.insert(0, ".data")

        for var in variaveis_usadas:
            data_section.append(f"{var}: .double 0.0")

    asm_final = "\n".join(text_section)

    if data_section:
        asm_final += "\n\n" + "\n".join(data_section)

    return asm_final


def ehNumero(token):
    try:
        float(token)
        return True
    except:
        return False