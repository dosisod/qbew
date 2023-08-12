from dataclasses import dataclass, field


class Type:
    def __str__(self) -> str:
        raise NotImplementedError()


class BaseType(Type): pass


class WordType(BaseType):
    def __str__(self) -> str:
        return "w"


class LongType(BaseType):
    def __str__(self) -> str:
        return "l"


class SingleType(BaseType):
    def __str__(self) -> str:
        return "s"


class DoubleType(BaseType):
    def __str__(self) -> str:
        return "d"


class ExtendedType(BaseType):
    def __str__(self) -> str:
        raise NotImplementedError()


class ByteType(ExtendedType):
    def __str__(self) -> str:
        return "b"


class HalfWordType(ExtendedType):
    def __str__(self) -> str:
        return "h"


class Statement:
    def __str__(self) -> str:
        raise NotImplementedError()


class Expression:
    type: Type

    def __str__(self) -> str:
        raise NotImplementedError()


@dataclass
class IntExpression(Expression):
    value: int
    type: Type = field(default_factory=WordType)

    def __str__(self) -> str:
        return str(self.value)


@dataclass
class StrExpression(Expression):
    value: str
    type: Type = field(default_factory=ByteType)

    def __str__(self) -> str:
        escaped = ascii(self.value).replace('"', r'\"')

        return f'"{escaped[1:-1]}"'


@dataclass
class ReturnStatement(Statement):
    expr: Expression

    def __str__(self) -> str:
        return f"ret {self.expr}"


@dataclass
class Block:
    name: str
    stmts: list[Statement] = field(default_factory=list)

    def __str__(self) -> str:
        stmts = "\n".join(f"\t{stmt}" for stmt in self.stmts)

        return f"@{self.name}\n{stmts}"


@dataclass
class Function:
    name: str
    rtype: Type
    blocks: list[Block] = field(default_factory=list)
    export: bool = False

    def __str__(self) -> str:
        export = "export " if self.export else ""
        header = f"{export}function {self.rtype} ${self.name}"

        blocks = "\n".join(str(block) for block in self.blocks)

        return f"{header}() {{\n{blocks}\n}}"


@dataclass
class Data:
    name: str
    items: list[Expression]

    def __str__(self) -> str:
        items = ", ".join(f"{expr.type} {expr}" for expr in self.items)

        return f"data ${self.name} = {{ {items} }}"


class Context:
    functions: list[Function]
    data: list[Data]

    def __init__(self) -> None:
        self.functions = []
        self.data = []

    def __str__(self) -> str:
        data = "\n".join(str(x) for x in self.data)
        funcs = "\n".join(str(x) for x in self.functions)

        return f"{data}\n{funcs}"

    def add_func(self, func: Function) -> None:
        self.functions.append(func)

    def add_data(self, data: Data) -> None:
        self.data.append(data)
