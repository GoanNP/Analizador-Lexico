def gerarAssembly(tokens):
    text_section = []
    data_section = []
    stack = []
    reg_count = 0
    label_count = 0
    tmp_count = 0

    def novo_reg():
        nonlocal reg_count
        if reg_count > 10:
            raise Exception("Estouro de registradores")
        r = f"R{reg_count}"
        reg_count += 1
        return r

    def novo_label():
        nonlocal label_count
        l = f"L{label_count}"
        label_count += 1
        return l

    text_section.append(".global _start")
    text_section.append(".text")
    text_section.append("_start:")

    variaveis_usadas = set()

    for token in tokens:

        if ehNumero(token):
            r = novo_reg()
            text_section.append(f"    MOV {r}, #{int(float(token))}")
            stack.append(r)

        elif token in ["RES", "MEM"]:
            r = novo_reg()
            text_section.append(f"    LDR {r}, ={token}")
            text_section.append(f"    LDR {r}, [{r}]")
            stack.append(r)
            variaveis_usadas.add(token)

        elif token in ["+", "-", "*", "/", "//", "%", "^"]:
            if len(stack) < 2 and token != "^":
                raise Exception("Erro: pilha insuficiente para operação")
            r_dest = novo_reg()
            tmp_var = f"TMP{tmp_count}"
            tmp_count += 1
            variaveis_usadas.add(tmp_var)

            if token in ["+", "-", "*"]:
                r2 = stack.pop()
                r1 = stack.pop()
                if token == '+':
                    text_section.append(f"    ADD {r_dest}, {r1}, {r2}")
                elif token == '-':
                    text_section.append(f"    SUB {r_dest}, {r1}, {r2}")
                elif token == '*':
                    text_section.append(f"    MUL {r_dest}, {r1}, {r2}")

                r_addr = novo_reg()
                text_section.append(f"    LDR {r_addr}, ={tmp_var}")
                text_section.append(f"    STR {r_dest}, [{r_addr}]")
                stack.append(r_dest)

            elif token in ["/", "//"]:
                r2 = stack.pop()
                r1 = stack.pop()
                r_temp = novo_reg()

                loop_label = novo_label()
                end_label = novo_label()

                text_section.append(f"    MOV {r_dest}, #0")
                text_section.append(f"    MOV {r_temp}, {r1}")

                text_section.append(f"{loop_label}:")
                text_section.append(f"    CMP {r_temp}, {r2}")
                text_section.append(f"    BLT {end_label}")
                text_section.append(f"    SUB {r_temp}, {r_temp}, {r2}")
                text_section.append(f"    ADD {r_dest}, {r_dest}, #1")
                text_section.append(f"    B {loop_label}")
                text_section.append(f"{end_label}:")

                r_addr = novo_reg()
                text_section.append(f"    LDR {r_addr}, ={tmp_var}")
                text_section.append(f"    STR {r_dest}, [{r_addr}]")
                stack.append(r_dest)

            elif token == "%":
                r2 = stack.pop()
                r1 = stack.pop()
                r_temp = novo_reg()

                loop_label = novo_label()
                end_label = novo_label()

                text_section.append(f"    MOV {r_dest}, #0")   # quociente
                text_section.append(f"    MOV {r_temp}, {r1}") # resto

                text_section.append(f"{loop_label}:")
                text_section.append(f"    CMP {r_temp}, {r2}")
                text_section.append(f"    BLT {end_label}")
                text_section.append(f"    SUB {r_temp}, {r_temp}, {r2}")
                text_section.append(f"    ADD {r_dest}, {r_dest}, #1")
                text_section.append(f"    B {loop_label}")
                text_section.append(f"{end_label}:")

                r_addr = novo_reg()
                text_section.append(f"    LDR {r_addr}, ={tmp_var}")
                text_section.append(f"    STR {r_temp}, [{r_addr}]")
                stack.append(r_temp)

            elif token == "^":
                if len(stack) < 2:
                    raise Exception("Erro: pilha insuficiente para potência")
                r_exp = stack.pop()
                r_base = stack.pop()
                r_result = r_dest

                loop_label = novo_label()
                end_label = novo_label()

                text_section.append(f"    MOV {r_result}, #1")
                text_section.append(f"{loop_label}:")
                text_section.append(f"    CMP {r_exp}, #0")
                text_section.append(f"    BEQ {end_label}")
                text_section.append(f"    MUL {r_result}, {r_result}, {r_base}")
                text_section.append(f"    SUB {r_exp}, {r_exp}, #1")
                text_section.append(f"    B {loop_label}")
                text_section.append(f"{end_label}:")

                r_addr = novo_reg()
                text_section.append(f"    LDR {r_addr}, ={tmp_var}")
                text_section.append(f"    STR {r_result}, [{r_addr}]")
                stack.append(r_result)

    if stack:
        r_result = stack[-1]
        variaveis_usadas.add("RES")
        r_addr = novo_reg()
        text_section.append(f"    LDR {r_addr}, =RES")
        text_section.append(f"    STR {r_result}, [{r_addr}]")

    text_section.append("    B .")

    if variaveis_usadas:
        data_section.append(".data")
        for var in variaveis_usadas:
            data_section.append(f"{var}: .word 0")

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