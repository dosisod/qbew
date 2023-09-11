import os
import subprocess
from pathlib import Path
from tempfile import mkstemp

from qbew.nodes import Context


def execute_context(ctx: Context) -> None:
    asm = ir_to_assembly(str(ctx))
    filename = compile_assembly(asm)

    try:
        subprocess.run([filename], check=False)

    finally:
        filename.unlink()


def ir_to_assembly(ir: str) -> str:
    process = subprocess.run(
        ["qbe", "-"],
        input=ir.encode(),
        # TODO: throw custom exception instead
        check=True,
        stdout=subprocess.PIPE,
    )

    return process.stdout.decode()


def compile_assembly(asm: str, file: Path | None = None) -> Path:
    if file is None:
        fd, filename = mkstemp()
        os.close(fd)
    else:
        filename = str(file)

    subprocess.run(
        ["cc", "-x", "assembler", "-", "-o", filename],
        input=asm.encode(),
        check=True,
    )

    binary = Path(filename)
    binary.chmod(0o755)

    return binary
