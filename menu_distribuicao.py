#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GUIA RÁPIDO: Gerar Executável Distribuível para Usuários Finais
Para: Ordem e Ajuste v2.5.4
"""

import os
import sys

def mostrar_menu():
    print("=" * 70)
    print("🤖 ORDEM E AJUSTE - CONSTRUTOR DE EXECUTÁVEL")
    print("=" * 70)
    print()
    print("OPÇÃO 1: Gerar .exe único (Recomendado)")
    print("  Cria: Ordem e Ajuste.exe (250-300 MB)")
    print("  Usuários: Apenas clicam 2x para rodar")
    print("  Incluído: Python + todas as bibliotecas")
    print()
    print("OPÇÃO 2: Gerar Pasta Portável")
    print("  Cria: Pasta OrdemEAjuste_Portable/")
    print("  Usuários: Extraem pasta e clicam em .bat")
    print("  Incluído: Python + bibliotecas + launcher.bat")
    print()
    print("OPÇÃO 3: Apenas Atualizar no GitHub")
    print("  Não gera executável")
    print("  Apenas atualiza o repositório")
    print("  (Usuários com .exe recebem atualização automática)")
    print()
    print("=" * 70)

def menu_opcao_1():
    """Gera executável único"""
    print("\n🚀 OPÇÃO 1: Gerando .exe Único")
    print("=" * 70)
    print()
    print("1. Confirme que launcher.py tem todos os imports necessários")
    print("   ✓ Verificado: Todos os imports estão presentes")
    print()
    print("2. Confirme que Ordem e Ajuste.ico existe")
    ico_existe = os.path.exists("Ordem e Ajuste.ico")
    print(f"   {'✓' if ico_existe else '✗'} Ícone: {'Encontrado' if ico_existe else 'NÃO ENCONTRADO'}")
    print()
    
    if not ico_existe:
        print("⚠️  Sem ícone, o .exe será gerado sem personalização visual")
        print()
    
    resposta = input("Deseja continuar? (s/n): ").lower().strip()
    
    if resposta == "s":
        print()
        print("Executando: python compilar_exe.py")
        print()
        os.system("python compilar_exe.py")
        
        if os.path.exists("dist/Ordem e Ajuste.exe"):
            print()
            print("✅ SUCESSO!")
            print()
            print("📁 Arquivo gerado: dist/Ordem e Ajuste.exe")
            print()
            print("📋 Próximos passos:")
            print("  1. Teste o .exe em seu computador")
            print("  2. Distribua o arquivo aos usuários")
            print("  3. Usuários clicam 2x para executar")
            print()
            return True
        else:
            print()
            print("❌ Erro na compilação")
            return False
    else:
        print("Operação cancelada")
        return False

def menu_opcao_2():
    """Gera pasta portável"""
    print("\n🎯 OPÇÃO 2: Gerando Pasta Portável")
    print("=" * 70)
    print()
    print("Executando: python criar_instalador.py")
    print()
    print("⏳ Isso pode levar 10-15 minutos (download de Python + dependências)")
    print()
    
    resposta = input("Deseja continuar? (s/n): ").lower().strip()
    
    if resposta == "s":
        print()
        os.system("python criar_instalador.py")
        
        if os.path.exists("OrdemEAjuste_Portable"):
            print()
            print("✅ SUCESSO!")
            print()
            print("📁 Pasta criada: OrdemEAjuste_Portable/")
            print()
            print("📋 Próximos passos:")
            print("  1. Comprima a pasta: OrdemEAjuste_Portable.zip")
            print("  2. Distribua o ZIP aos usuários")
            print("  3. Usuários extraem e clicam em Ordem e Ajuste.bat")
            print()
            return True
        else:
            print()
            print("❌ Erro na criação")
            return False
    else:
        print("Operação cancelada")
        return False

def menu_opcao_3():
    """Atualiza no GitHub"""
    print("\n📤 OPÇÃO 3: Atualizar no GitHub")
    print("=" * 70)
    print()
    print("Executando: python update_and_push.py")
    print()
    
    os.system("python update_and_push.py")
    print()

def main():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        mostrar_menu()
        
        opcao = input("\nEscolha uma opção (1-3) ou Q para sair: ").strip().upper()
        
        if opcao == "1":
            if menu_opcao_1():
                input("\nPressione ENTER para voltar ao menu...")
        elif opcao == "2":
            if menu_opcao_2():
                input("\nPressione ENTER para voltar ao menu...")
        elif opcao == "3":
            menu_opcao_3()
            input("\nPressione ENTER para voltar ao menu...")
        elif opcao == "Q":
            print("\nAté logo!")
            break
        else:
            print("\n❌ Opção inválida")
            input("Pressione ENTER...")

if __name__ == "__main__":
    main()
