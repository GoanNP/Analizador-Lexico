def gerarAssembly(tokens):
    asm = []
    stack = []
    reg_count = 0

    def novo_reg():
        nonlocal reg_count
        r = f"R{reg_count}"
        reg_count += 1
        return r

    for token in tokens:

        if float(token):
            r = novo_reg()
            asm.append(f"MOV {r}, #{token}")
            stack.append(r)

        elif token in ["RES", "MEM"]:
            r = novo_reg()
            asm.append(f"LDR {r}, ={token}")
            stack.append(r)

        elif token in ["+", "-", "*", "/", "//", "%", "^"]:
            r2 = stack.pop()
            r1 = stack.pop()
            r_dest = novo_reg()

            if token == '+':
                asm.append(f"ADD {r_dest}, {r1}, {r2}")
            elif token == '-':
                asm.append(f"SUB {r_dest}, {r1}, {r2}")
            elif token == '*':
                asm.append(f"MUL {r_dest}, {r1}, {r2}")
            elif token == '/':
                asm.append(f"SDIV {r_dest}, {r1}, {r2}")
            elif token == '//':
                asm.append(f"SDIV {r_dest}, {r1}, {r2}")
            elif token == '%':
                r_temp = novo_reg()
                asm.append(f"SDIV {r_temp}, {r1}, {r2}")
                asm.append(f"MUL {r_temp}, {r_temp}, {r2}")
                asm.append(f"SUB {r_dest}, {r1}, {r_temp}")
            elif token == '^':
                asm.append(f"; potência não implementada diretamente")

            stack.append(r_dest)

    return "\n".join(asm)