def gerarAssembly(tokens):
    text_section = []
    data_section = []
    stack = []

    reg_int = 0
    reg_double = 0
    label_count = 0
    const_count = 0
    variaveis_usadas = set()

    def novo_reg_int():
        nonlocal reg_int
        r = f"R{reg_int % 12}"
        reg_int += 1
        return r

    def novo_reg_double():
        nonlocal reg_double
        r = f"D{reg_double % 16}"
        reg_double += 1
        return r

    def novo_label():
        nonlocal label_count
        l = f"L{label_count}"
        label_count += 1
        return l

    def reset_registradores():
        nonlocal reg_int, reg_double
        reg_int = 0
        reg_double = 0

    def garantir_double(reg, tipo):
        if tipo == "double":
            return reg

        s = "S0"
        d = novo_reg_double()

        text_section.append(f"    VMOV {s}, {reg}")
        text_section.append(f"    VCVT.F64.S32 {d}, {s}")

        return d

    def salvar_em_MEM():
        if not stack:
            return

        (reg, tipo) = stack[-1]

        r_addr = novo_reg_int()
        text_section.append(f"    LDR {r_addr}, =MEM")

        if tipo == "double":
            text_section.append(f"    VSTR.F64 {reg}, [{r_addr}]")
        else:
            text_section.append(f"    VMOV S0, {reg}")
            text_section.append(f"    VCVT.F64.S32 D0, S0")
            text_section.append(f"    VSTR.F64 D0, [{r_addr}]")

    def mostrar_no_display():
        r_addr = novo_reg_int()
        d_val = novo_reg_double()

        text_section.append(f"    LDR {r_addr}, =MEM")
        text_section.append(f"    VLDR {d_val}, [{r_addr}]")

        r_val = novo_reg_int()
        text_section.append(f"    VCVT.S32.F64 S0, {d_val}")
        text_section.append(f"    VMOV {r_val}, S0")


        r_temp = novo_reg_int()
        text_section.append(f"    MOV {r_temp}, {r_val}")

        r_uni = novo_reg_int()
        r_dez = novo_reg_int()
        r_cent = novo_reg_int()
        r_mil = novo_reg_int()

        text_section.append(f"    MOV {r_uni}, #0")
        text_section.append(f"    MOV {r_dez}, #0")
        text_section.append(f"    MOV {r_cent}, #0")
        text_section.append(f"    MOV {r_mil}, #0")

        loop_u = novo_label()
        end_u = novo_label()

        text_section.append(f"{loop_u}:")
        text_section.append(f"    CMP {r_temp}, #10")
        text_section.append(f"    BLT {end_u}")
        text_section.append(f"    SUB {r_temp}, {r_temp}, #10")
        text_section.append(f"    ADD {r_dez}, {r_dez}, #1")
        text_section.append(f"    B {loop_u}")
        text_section.append(f"{end_u}:")
        text_section.append(f"    MOV {r_uni}, {r_temp}")

        r_temp2 = novo_reg_int()
        text_section.append(f"    MOV {r_temp2}, {r_dez}")
        text_section.append(f"    MOV {r_dez}, #0")

        loop_d = novo_label()
        end_d = novo_label()

        text_section.append(f"{loop_d}:")
        text_section.append(f"    CMP {r_temp2}, #10")
        text_section.append(f"    BLT {end_d}")
        text_section.append(f"    SUB {r_temp2}, {r_temp2}, #10")
        text_section.append(f"    ADD {r_cent}, {r_cent}, #1")
        text_section.append(f"    B {loop_d}")
        text_section.append(f"{end_d}:")
        text_section.append(f"    MOV {r_dez}, {r_temp2}")

        r_temp3 = novo_reg_int()
        text_section.append(f"    MOV {r_temp3}, {r_cent}")
        text_section.append(f"    MOV {r_cent}, #0")

        loop_c = novo_label()
        end_c = novo_label()

        text_section.append(f"{loop_c}:")
        text_section.append(f"    CMP {r_temp3}, #10")
        text_section.append(f"    BLT {end_c}")
        text_section.append(f"    SUB {r_temp3}, {r_temp3}, #10")
        text_section.append(f"    ADD {r_mil}, {r_mil}, #1")
        text_section.append(f"    B {loop_c}")
        text_section.append(f"{end_c}:")
        text_section.append(f"    MOV {r_cent}, {r_temp3}")

        tabela = [
            "0x3F","0x06","0x5B","0x4F","0x66",
            "0x6D","0x7D","0x07","0x7F","0x6F"
        ]

        data_section.append("SEG_TABLE:")
        for val in tabela:
            data_section.append(f"    .word {val}")

        r_table = novo_reg_int()
        text_section.append(f"    LDR {r_table}, =SEG_TABLE")


        def conv(dig_reg):
            r_code = novo_reg_int()
            text_section.append(f"    LDR {r_code}, [{r_table}, {dig_reg}, LSL #2]")
            return r_code

        r_u_code = conv(r_uni)
        r_d_code = conv(r_dez)
        r_c_code = conv(r_cent)
        r_m_code = conv(r_mil)


        text_section.append(f"    LSL {r_d_code}, {r_d_code}, #8")
        text_section.append(f"    LSL {r_c_code}, {r_c_code}, #16")
        text_section.append(f"    LSL {r_m_code}, {r_m_code}, #24")

        text_section.append(f"    ORR {r_u_code}, {r_u_code}, {r_d_code}")
        text_section.append(f"    ORR {r_u_code}, {r_u_code}, {r_c_code}")
        text_section.append(f"    ORR {r_u_code}, {r_u_code}, {r_m_code}")



        r_disp = novo_reg_int()
        text_section.append(f"    LDR {r_disp}, =0xFF200020")
        text_section.append(f"    STR {r_u_code}, [{r_disp}]")


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

    def operacao_aritmetica(op):
        (r2, t2) = stack.pop()
        (r1, t1) = stack.pop()

        r1 = garantir_double(r1, t1)
        r2 = garantir_double(r2, t2)

        r_dest = novo_reg_double()

        op_map = {
            "+": "VADD.F64",
            "-": "VSUB.F64",
            "*": "VMUL.F64",
            "/": "VDIV.F64"
        }

        text_section.append(f"    {op_map[op]} {r_dest}, {r1}, {r2}")
        stack.append((r_dest, "double"))

        salvar_em_MEM()

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

        salvar_em_MEM()

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

        salvar_em_MEM()

    def operacao_mem_load(mem):
        d = novo_reg_double()
        r = novo_reg_int()

        text_section.append(f"    LDR {r}, ={mem}")
        text_section.append(f"    VLDR {d}, [{r}]")

        stack.append((d, "double"))
        variaveis_usadas.add(mem)

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

    text_section.append(".global _start")
    text_section.append(".text")
    text_section.append("_start:")

    processar(tokens)

    reset_registradores()
    mostrar_no_display()

    text_section.append("    B .")

    if data_section or variaveis_usadas:
        data_section.insert(0, ".data")
        data_section.append("MEM: .double 0.0")

        for var in variaveis_usadas:
            if var != "MEM":
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