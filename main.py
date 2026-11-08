import ast

class PythonToAssemblyCompiler(ast.NodeVisitor):
    def __init__(self):
        self.code = []
        self.data_section = []
        self.label_counter = 0

    def new_label(self, name):
        self.label_counter += 1
        return f"_{name}_{self.label_counter}"

    def compile(self, source_code):
        tree = ast.parse(source_code)
        
        # 어셈블리 템플릿 기본 구조 (Linux x86-64 기준)
        self.code.append("section .text")
        self.code.append("global main")
        self.code.append("main:")
        self.code.append("    push rbp")
        self.code.append("    mov rbp, rsp")
        
        # AST 순회 시작
        self.visit(tree)
        
        # 프로그램 종료 (exit syscall)
        self.code.append("    mov rax, 60")
        self.code.append("    xor rdi, rdi")
        self.code.append("    syscall")
        
        return "\n".join(self.code)

    def visit_Assign(self, node):
        # 변수 할당: x = 10 -> rax에 값을 넣고 스택 메모리에 저장
        self.visit(node.value) # 결과를 rax에 담음
        # 간단히 하기 위해 변수명을 스택 오프셋(-8, -16 등)에 매핑한다고 가정
        # 실제 구현에서는 심볼 테이블(Symbol Table)이 필요합니다.
        self.code.append("    push rax")

    def visit_BinOp(self, node):
        # 사칙연산 처리 (+)
        self.visit(node.right)
        self.code.append("    push rax")
        self.visit(node.left)
        self.code.append("    pop rbx")
        
        if isinstance(node.op, ast.Add):
            self.code.append("    add rax, rbx")
        elif isinstance(node.op, ast.Sub):
            self.code.append("    sub rax, rbx")
        elif isinstance(node.op, ast.Mult):
            self.code.append("    imul rax, rbx")

    def visit_Constant(self, node):
        # 정수 상수 처리: rax 레지스터에 값 로드
        if isinstance(node.value, int):
            self.code.append(f"    mov rax, {node.value}")

    def visit_If(self, node):
        # 조건문 (if) 처리
        else_label = self.new_label("else")
        end_label = self.new_label("endif")

        # 조건식 평가 (예: a < b)
        self.visit(node.test)
        self.code.append("    cmp rax, 0")
        self.code.append(f"    je {else_label}")

        # 본문(Body) 실행
        for stmt in node.body:
            self.visit(stmt)
        self.code.append(f"    jmp {end_label}")

        # Else 블록
        self.code.append(f"{else_label}:")
        if node.orelse:
            for stmt in node.orelse:
                self.visit(stmt)

        self.code.append(f"{end_label}:")

# 사용 예시
python_code = """
your_python_code
"""

compiler = PythonToAssemblyCompiler()
assembly_output = compiler.compile(python_code)
print(assembly_output)
