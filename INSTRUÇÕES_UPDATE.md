# Sistema de Atualização Automática

## Como Fazer Upload do .exe no GitHub

### 1. Criar uma Release no GitHub

1. Acesse: https://github.com/JhonatasPSoares/ordem-e-ajuste/releases
2. Clique em "Create a new release"
3. Preencha:
   - **Tag version:** `latest`
   - **Release title:** `Transferencia.01 v1.0`
   - **Description:** Descrição das mudanças
4. Clique em "Attach binaries"
5. Arraste o arquivo `dist/Transferencia.01.exe`
6. Clique em "Publish release"

### 2. URL do .exe será:
```
https://github.com/JhonatasPSoares/ordem-e-ajuste/releases/download/latest/Transferencia.01.exe
```

### 3. Verificar Atualizações

Quando um usuário abre o `.exe`:
- ✅ Valida o `app_version.json` no GitHub
- ✅ Se `hash == "exe_build"`, baixa a nova versão
- ✅ Mostra barra de progresso durante download
- ✅ Pede para reiniciar o app
- ✅ Carrega a nova versão automaticamente

## Fluxo Completo de Atualização

```
Você faz mudança no código
        ↓
python update_and_push.py
        ↓
Detecta mudança de dependências?
        ↓
    SIM → Gera novo .exe
           Faz upload na Release
           git push
        ↓
Usuário abre o .exe
        ↓
App baixa e atualiza sozinho
        ↓
Mostra barra de progresso
        ↓
Reinicia com nova versão
```

## Importante

- Sempre use a tag `latest` nas releases
- O arquivo deve estar nomeado exatamente: `Transferencia.01.exe`
- A URL no código deve apontar para essa release
