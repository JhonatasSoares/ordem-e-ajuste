# 🤖 Ordem e Ajuste - Instruções de Distribuição

## Versão Atual
**2.5.4**

## Para Desenvolvedores: Gerar Executável

### Pré-requisitos
```bash
pip install pyinstaller requests pandas selenium undetected-chromedriver ttkbootstrap keyboard pyautogui
```

### Gerar o .exe

Execute o script de compilação:
```bash
python compilar_exe.py
```

Isso criará: `dist/Ordem e Ajuste.exe`

**O que está incluído no .exe:**
- Python 3.x embarcado
- Todas as bibliotecas necessárias
- Ícone personalizado
- Sem necessidade de Python instalado no PC

### Tamanho
~250-300 MB (tudo auto-contido)

---

## Para Usuários Finais: Como Usar

### Opção 1: Executável Simples
1. Baixe `Ordem e Ajuste.exe`
2. Clique duas vezes para executar
3. Pronto! O app inicia automaticamente

**Requisitos:**
- Windows 7 ou superior (64-bit)
- Conexão com internet
- ~500MB livres em disco

### Opção 2: Pasta Portável
1. Extraia a pasta `OrdemEAjuste_Portable`
2. Clique em `Ordem e Ajuste.bat`
3. O aplicativo inicia

---

## 🔄 Sistema de Atualizações

O aplicativo verifica automaticamente por atualizações no GitHub:
- Ao iniciar, baixa a versão mais recente
- Sem necessidade de reinstalar
- Usa hash SHA256 para verificar mudanças

---

## 📁 Estrutura do Projeto

```
c:\Users\...\Code Ordem e ajuste\
├── Transferencia.01.py          (Aplicativo principal)
├── launcher.py                  (Carregador - incluir no .exe)
├── app_version.json             (Controle de versão)
├── compilar_exe.py              (Script para gerar .exe)
├── update_and_push.py           (Script para atualizar no GitHub)
├── Ordem e Ajuste.bat           (Launcher para Windows)
├── Ordem e Ajuste.ico           (Ícone)
├── .gitignore                   (Protege arquivos sensíveis)
└── README.md                    (Este arquivo)
```

---

## 🚀 Fluxo de Atualização para Desenvolvedores

### 1. Fazer Alterações
Edite `Transferencia.01.py` normalmente

### 2. Atualizar no GitHub
```bash
python update_and_push.py
```
Digite uma mensagem de commit e ENTER

### 3. Atualizar Executável (Opcional)
Se necessário atualizar o .exe com novas dependências:
```bash
python compilar_exe.py
```

### 4. Distribuir
- Executável: Use o arquivo `dist/Ordem e Ajuste.exe`
- Portável: Use a pasta `OrdemEAjuste_Portable`

---

## ⚙️ Detalhes Técnicos

### Como o Launcher Funciona
1. `launcher.py` é compilado em um .exe
2. Ao executar, o .exe tem Python embarcado
3. Baixa `Transferencia.01.py` do GitHub
4. Executa o código com `exec()` (tudo no mesmo processo)
5. A interface Tkinter abre normalmente

### Por que `exec()` ao invés de subprocess?
- `subprocess` precisaria de Python instalado
- `exec()` roda direto no interpretador do .exe
- Funciona sem nenhuma dependência externa

---

## 📦 Checklist para Distribuição

- [ ] Testar o .exe em PC sem Python instalado
- [ ] Verificar se o app atualiza corretamente do GitHub
- [ ] Incluir instruções de uso no email
- [ ] Confirmar que usuários conseguem executar
- [ ] Documentar credenciais em `usuario.json`

---

## 🆘 Troubleshooting

### "Arquivo não encontrado"
- Verifique se o GitHub tem o arquivo correto
- Confirme a URL em `launcher.py` está correta

### "Erro de conexão"
- Verifique conexão com internet
- Pode ser bloqueio de firewall
- Tente usar VPN se necessário

### "Permissão negada"
- Tente executar como Administrador
- Verifique espaço em disco disponível

---

**Versão:** 2.5.4  
**Repositório:** https://github.com/JhonatasSoares/ordem-e-ajuste  
**Criado por:** JhonatasSoares
