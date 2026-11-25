# 🖥️ Inventário de PC

Script em **Python** que coleta as principais informações de um computador e gera um relatório pronto para o **suporte de TI**: sistema operacional, processador, memória RAM, discos (com alerta de pouco espaço) e IP local.

## Por que esse projeto?
No dia a dia do suporte, é comum precisar levantar a configuração de uma máquina antes de um atendimento ou para controle de patrimônio. Este script faz isso em segundos, sem instalar nada.

## Como usar
Requisito: Python 3.10 ou superior (só a biblioteca padrão, funciona em Windows e Linux).

```bash
python inventario.py            # mostra o relatório na tela
python inventario.py --salvar   # também salva em .txt e .json
```

Exemplo de saída:
```
==================================================
 INVENTÁRIO DE PC - MEU-PC
==================================================
Sistema .......... Windows 11
Processador ...... Intel64 Family 6 Model 140
Núcleos lógicos .. 8
Memória RAM ...... 15.7 GB
IP local ......... 192.168.0.10

Discos:
  C:\     120.4 GB livres de 237.3 GB (49.3% usado)
```

## O que pratiquei
- Módulos `platform`, `socket`, `shutil` e `os`
- Chamada à API do Windows com `ctypes` para ler a memória
- Geração de relatórios em texto e JSON
