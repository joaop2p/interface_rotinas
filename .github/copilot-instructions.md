# Gerenciador de Rotinas - Instruções para IA

## Contexto

Esta aplicação é um **gerenciador de scripts Python** desenvolvido para organizar e executar rotinas de automação de forma visual e centralizada. O objetivo principal é permitir que usuários categorizem seus scripts, executem-nos através de uma interface gráfica amigável e monitorem a saída em tempo real.

### Propósito
- **Organização**: Scripts organizados por categorias personalizáveis com ícones
- **Execução Simplificada**: Interface gráfica para executar scripts sem linha de comando
- **Monitoramento**: Terminal integrado com logs em tempo real da execução
- **Gestão**: CRUD completo de categorias e rotinas com validações

### Público-Alvo
Desenvolvedores e usuários técnicos que possuem múltiplos scripts Python para tarefas diversas (automação, análise de dados, utilitários, etc.) e desejam uma forma organizada de gerenciá-los.

### Arquitetura de Deploy
Aplicação desktop standalone para Windows que armazena dados localmente no `AppData` do usuário, sem dependências externas além do Python e suas bibliotecas.

## Visão Geral da Arquitetura

Esta é uma aplicação desktop Python construída com **Flet** para interface gráfica e **SQLModel** para operações de banco de dados. O app gerencia e executa scripts Python (rotinas) organizados por categorias.

### Componentes Principais

- **Ponto de Entrada**: `main.py` → `lib/app/myapp.py` → `PageManager` (padrão singleton)
- **Roteamento**: `PageManager` gerencia navegação SPA com constantes `Routes`
- **Views**: Todas herdam de `ViewTemplate` com métodos `get_view()` e `set_page()`
- **Camada de Dados**: Padrão Controller → Service → DAO com SQLModel/SQLite
- **Banco de Dados**: SQLite com chaves estrangeiras habilitadas, triggers automáticos para `dt_modified`
- **Terminal de Logs**: `InMemoryLogHandler` captura logs em tempo real para exibição na UI

### Modelos e Relacionamentos do Banco

```python
# Um-para-muitos: Category → Routines
Category: category_id (PK), category_name (unique), icon
Routine: routine_id (PK), routine_name, directory_path, description, category_id (FK), dt_created, dt_modified
```

## Padrões Críticos

### 1. Ciclo de Vida das Views
- Views usam **carregamento assíncrono** com `_page.run_task()` para operações de dados
- Todas as views devem chamar `set_page()` antes de `get_view()`
- Use `ft.Ref[ComponentType]()` para atualizações dinâmicas de conteúdo

### 2. Componentes Singleton
- `DatabaseConfig`: Gerenciador de conexão de banco thread-safe
- `PageManager`: Gerencia toda navegação e estado das views
- `LoggerConfig`: Logging centralizado com captura in-memory para terminal da UI

### 3. Execução de Rotinas
Use o serviço `RoutineRunner` para executar scripts Python:
```python
runner = RoutineRunner()
runner.run(script_path, on_line=callback_func, hide_console=True)
```

### 4. Exibição de Logs em Tempo Real
Views se inscrevem em logs via `InMemoryLogHandler` com saída tipo terminal:
```python
self._page.pubsub.subscribe(lambda m: self._update_terminal(m["text"]))
```

## Comandos de Desenvolvimento

```powershell
# Executar aplicação
python main.py

# Banco é criado automaticamente em: C:\users\{user}\AppData\Local\Scripts Hub\database\rotinas.sqlite
```

## Regras de Organização de Arquivos

- **Controllers**: Camada fina de validação, delegam para Services
- **Services**: Lógica de negócio, coordenam entre Controllers e DAOs
- **DAOs**: Operações diretas de banco usando SQLModel Sessions
- **Views**: Componentes de UI em `views/` com widgets reutilizáveis em `views/widgets/`
- **Models**: `db/models.py` para tabelas SQLModel, `interfaces/` para abstrações

## Convenções Importantes

1. **Tratamento de Erros**: Use exceções específicas (ex: `CategoryInUseError`)
2. **Logging**: Todos os componentes obtêm logger via `logging.getLogger(component_name)`
3. **Constantes**: Centralizadas em `AppConstants`, `SQLConstants`, `LogMessages`
4. **Operações Assíncronas**: Use `asyncio.Task` para operações longas nas views
5. **Validação de Arquivos**: Scripts devem ter extensões Python de `AppConstants.PYTHON_EXTENSIONS`

## Pontos de Integração

- **Framework Flet**: Toda UI construída com componentes Flet e padrões assíncronos
- **Banco SQLite**: Chaves estrangeiras habilitadas, triggers automáticos de timestamp
- **Sistema de Arquivos**: Execução de scripts Python com captura de saída em tempo real
- **Integração Windows**: App desktop com armazenamento local no AppData

## Fluxo de Navegação

Home (`/home`) → Adicionar Categoria (`/add_category`) / Adicionar Rotina (`/add_routine`) / Detalhes da Rotina (`/routine_details`)

Rotas gerenciadas pelo singleton `PageManager` com instanciação dinâmica de views para formulários.