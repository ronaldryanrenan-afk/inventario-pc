"""Inventário rápido de computador.

Coleta informações básicas da máquina (sistema, processador, memória, discos e rede)
e gera um relatório em texto e em JSON. Útil no suporte de TI para registrar
equipamentos ou levantar dados antes de um atendimento.

Uso:
    python inventario.py              # mostra o relatório na tela
    python inventario.py --salvar     # também salva relatorio_<nome-do-pc>.txt e .json
"""

import argparse
import json
import os
import platform
import shutil
import socket
import string
from datetime import datetime


def bytes_para_gb(valor: int) -> float:
    return round(valor / (1024 ** 3), 1)


def memoria_total_gb() -> float | None:
    """Memória RAM total. Usa a API do Windows ou /proc/meminfo no Linux."""
    if platform.system() == "Windows":
        import ctypes

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MEMORYSTATUSEX()
        status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
        return bytes_para_gb(status.ullTotalPhys)
    try:
        with open("/proc/meminfo") as f:
            kb = int(f.readline().split()[1])
        return bytes_para_gb(kb * 1024)
    except (OSError, ValueError, IndexError):
        return None


def discos() -> list[dict]:
    if platform.system() == "Windows":
        pontos = [f"{letra}:\\" for letra in string.ascii_uppercase if os.path.exists(f"{letra}:\\")]
    else:
        pontos = ["/"]
    resultado = []
    for ponto in pontos:
        try:
            uso = shutil.disk_usage(ponto)
        except OSError:
            continue
        resultado.append({
            "unidade": ponto,
            "total_gb": bytes_para_gb(uso.total),
            "livre_gb": bytes_para_gb(uso.free),
            "uso_percentual": round(uso.used / uso.total * 100, 1),
        })
    return resultado


def ip_local() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # não envia dados, só descobre a interface de saída
            return s.getsockname()[0]
    except OSError:
        return "indisponível"


def coletar() -> dict:
    return {
        "gerado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "nome_do_computador": socket.gethostname(),
        "sistema": f"{platform.system()} {platform.release()} ({platform.version()})",
        "arquitetura": platform.machine(),
        "processador": platform.processor() or "não identificado",
        "nucleos_logicos": os.cpu_count(),
        "memoria_ram_gb": memoria_total_gb(),
        "discos": discos(),
        "ip_local": ip_local(),
        "python": platform.python_version(),
    }


def formatar(info: dict) -> str:
    linhas = [
        "=" * 50,
        f" INVENTÁRIO DE PC - {info['nome_do_computador']}",
        "=" * 50,
        f"Gerado em ........ {info['gerado_em']}",
        f"Sistema .......... {info['sistema']}",
        f"Arquitetura ...... {info['arquitetura']}",
        f"Processador ...... {info['processador']}",
        f"Núcleos lógicos .. {info['nucleos_logicos']}",
        f"Memória RAM ...... {info['memoria_ram_gb']} GB",
        f"IP local ......... {info['ip_local']}",
        "",
        "Discos:",
    ]
    for d in info["discos"]:
        alerta = "  ⚠ pouco espaço" if d["uso_percentual"] >= 90 else ""
        linhas.append(
            f"  {d['unidade']:<5} {d['livre_gb']:>7} GB livres de {d['total_gb']} GB "
            f"({d['uso_percentual']}% usado){alerta}"
        )
    return "\n".join(linhas)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera um inventário rápido do computador")
    parser.add_argument("--salvar", action="store_true", help="salva o relatório em .txt e .json")
    args = parser.parse_args()

    info = coletar()
    texto = formatar(info)
    print(texto)

    if args.salvar:
        base = f"relatorio_{info['nome_do_computador']}"
        with open(f"{base}.txt", "w", encoding="utf-8") as f:
            f.write(texto)
        with open(f"{base}.json", "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        print(f"\nRelatórios salvos: {base}.txt e {base}.json")


if __name__ == "__main__":
    main()
