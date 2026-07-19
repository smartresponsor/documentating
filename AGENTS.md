# AGENTS.md

# SmartResponsor Platform Rules

Этот файл находится в корне репозитория и является постоянным контекстом для Codex CLI.
Перед работой прочитай также `README.md`, `composer.json`, `MANIFEST.json` и локальную `.gating/`, если она есть.

## 1. Источник текущего кода

- Работай с текущим деревом репозитория.
- Архив, переданный как «текущий срез», полностью заменяет предыдущие срезы.
- Предыдущий архив допустим только при полном совпадении SHA-256.
- Сначала составь краткий inventory текущего состояния, затем меняй код.
- Для удаления используй точный список подтверждённо устаревших файлов.

## 2. Runtime

- PHP `8.4+`.
- Symfony `8.x+`.
- Код использует возможности текущих PHP ^8.4 и Symfony ^8.*.
- Обратная совместимость с PHP ниже 8.4 и Symfony 7 не является целью.
- Основной namespace приложений и компонентов: `App\`.
- Каждый PHP-файл использует `declare(strict_types=1);`.
- Комментарии, docblock и технические тексты в коде пишутся на английском.

## 3. Symfony-oriented структура

Используй typed layers, которые читаются по имени класса и папке:

```text
*Entity       → src/Entity/
*EntityInterface       → src/EntityInterface/
*Repository   → src/Repository/
*RepositoryInterface   → src/RepositoryInterface/
*Controller   → src/Controller/
*ControllerInterface   → src/ControllerInterface/
*Type         → src/Form/
*TypeInterface         → src/TypeInterface/
*Voter        → src/Voter/
*VoterInterface        → src/VoterInterface/
*Subscriber   → src/EventSubscriber/ или src/Subscriber/
*SubscriberInterface   → src/EventSubscriberInterface/ или src/SubscriberInterface/
*Listener     → src/Listener/
*ListenerInterface     → src/ListenerInterface/
*Command      → src/Command/
*CommandInterface      → src/CommandInterface/
```

- Классы и методы получают предметные имена в единственном числе.
- Интерфейс описывает реальный публичный контракт.
- Описательные docblock сохраняют назначение, инварианты и эксплуатационный контекст.

Отдельные деревья `src/Domain`, `Port`, `Adapter`, `Adaptor`, `Resource`, `Surface` в платформе не используются.

## 4. Роль репозитория

Сначала определи роль репозитория по `composer.json`, `MANIFEST.json`, bundle-классу и текущему коду.

### Обычное приложение или компонент

- Хранит собственную бизнес-ответственность.
- Подключает общие возможности через Composer dependencies.
- Использует публичные контракты соседних компонентов.

### Cruding

- Владеет общей CRUD-механикой.
- Владеет generic CRUD routes и CRUD controllers.
- Владеет разбором URI и выбором CRUD operation.
- Владеет канонической CRUD route grammar.

### Objecting

- Владеет повторно используемыми системными полями.
- Владеет их Doctrine mapping, traits, interfaces и публичным API.
- Consumer Entity подключает Objecting pack вместо локальной копии системного поля.

### Gating

- Владеет исполняемыми правилами канонизации.
- `AGENTS.md` объясняет канон Codex; Gating проверяет его машинно.
- При расхождении правила синхронизируются в обоих местах, но AGENTS.md только расшмпением.

### Documentating

- Владеет полной общей документацией платформы.
- Каждый компонент хранит только документацию своей ответственности.

## 5. Zero CRUD controllers и zero CRUD routes YAML

Целевое состояние обычного приложения:

```text
zero CRUD controllers
zero CRUD routes YAML
```

Generic операции принадлежат Cruding:

```text
index
show
new
edit
delete
archive
restore
import
export
```

Обычное приложение предоставляет Cruding необходимые:

```text
Entity
Repository
Form Type
Service
```

Бизнес-маршруты остаются в приложении, которому принадлежит бизнес-действие. Например:

```text
approve
calculate
confirm
pay
publish
send
synchronize
```

Business route и business controller/service используются для реального бизнес-действия, а не для повторения generic CRUD.

Route grammar:

- первый сегмент показывает владельца или бизнес-сущность;
- каждое понятие занимает отдельный `/segment`;
- tokens используются в единственном числе;
- `id` или `slug` находятся только в конце URI;
- CRUD operation token находится перед `id` или `slug`;
- generic CRUD grammar реализуется в Cruding.

## 6. Подключаемые приложения

Каждый репозиторий имеет собственные:

```text
composer.json
composer.lock
установленные dependencies
```

Общие приложения подключаются явно, в частности:

```text
Cruding
Interfacing
Viewing
Objecting
```

Cruding, Interfacing и Viewing могут работать:

- внутри host application;
- как отдельно установленный component/application;
- на own site с собственным runtime.

Связь между соседними репозиториями выражается Composer dependency и публичным контрактом, а не наличием соседней папки.

## 7. Entity и поток данных

Doctrine Entity используется внутри операции, которая читает или изменяет её состояние.

Канонический поток:

1. HTTP, CLI, Messenger или webhook принимает scalar values и input DTO.
2. Application operation получает идентификатор и входные данные.
3. Repository загружает Entity рядом с этой операцией.
4. Бизнес-изменение выполняется внутри короткой операции и, когда нужно, Doctrine transaction.
5. Наружу возвращается result DTO, view model, scalar result или идентификатор.

Для внешних и асинхронных границ используй:

```text
id
slug
input DTO
message DTO
result DTO
```

Doctrine Entity остаётся внутри Doctrine/application boundary и не используется как универсальный transport payload для Messenger, session, webhook или внешнего API.

## 8. Транзакции и version

- Doctrine transaction охватывает одну короткую прикладную операцию.
- Внешний HTTP-вызов выполняется вне долгой database transaction.
- Mutable root Entity с риском lost update использует каноническое Objecting version field и Doctrine optimistic locking.
- `version` является технической версией состояния строки.
- Doctrine управляет увеличением версии.
- Expected version передаётся от чтения формы к сохранению и проверяется при update.
- Business revision или номер документа моделируется отдельным бизнес-полем.

## 9. User Vendor identity и системные поля

- `VendorEntity` является основной business root User Entity.
- `VendorEntity.id` является PostgreSQL primary key и сквозным идентификатором платформы.
- `VendorSecurityEntity` является OneToOne security extension.
- `VendorSecurityEntity` использует тот же shared primary key.
- Login, password hash и security metadata находятся в `VendorSecurityEntity`.
- Multitenancy платформы реализуется существующей Vendor identity.

Objecting предоставляет канонические lifecycle fields и методы для:

```text
created / createdBy
modified / modifiedBy
deleted / deletedBy
version
```

- Consumer Entity подключает актуальный Objecting pack.
- Реальная business relation к Vendor называется `vendor` или `vendor_id`.
- Отдельная Tenant identity не создаётся поверх Vendor identity.
- Поле `tenant_id` заменяется только после определения его реальной семантики.

## 10. Entity First database development

Текущий режим разработки — Entity First.

- Entity, Doctrine mapping, relations, constraints и indexes являются источником текущей схемы.
- Локальная development database перестраивается под текущую Entity-модель.
- Doctrine migrations сейчас не являются частью рабочего процесса, если задача прямо не требует иного.
- Текущая модель сразу заменяет старую модель.
- После переноса всех callers устаревшие aliases, wrappers и параллельные реализации удаляются.
- Doctrine mapping и фактическая локальная схема проверяются после изменения.

## 11. Локальная разработка и production

Канонический путь изменения:

```text
local repository
→ implementation
→ lint/static analysis/tests/Gating
→ Git
→ deployment
→ production
```

Production получает проверенный build или package. Разработка и исправление исходного кода выполняются локально.

## 12. UI и стили

Основные UI providers:

```text
AntDesign and ProComponent
PrimeReact
```

- Используй provider, уже выбранный текущим интерфейсом.
- Общие цвета, размеры, spacing и состояния задаются theme tokens, component styles или отдельными style-файлами.
- Inline CSS является редким локально обоснованным исключением.
- Новые интерфейсы собираются из существующих компонентов provider.

## 13. Документация

### Markdown (`.md`)

Используется для обычной репозиторной документации:

```text
README.md
CHANGELOG.md
CONTRIBUTING.md
короткие инструкции
локальные заметки
```

### AsciiDoc (`.adoc`)

Используется для структурированной документации:

```text
архитектура
спецификации
длинные руководства
операционные инструкции
публикуемая документация
```

AsciiDoc обрабатывается.

Маленький репозиторий документирует только собственную ответственность. Полная объединённая документация находится в Documentating.

## 14. Gating и качество

Gating является исполняемым каноном платформы.

Перед завершением задачи запусти доступные проверки текущего репозитория:

```text
Gating
composer validate
composer scripts
PHP syntax check
PHPStan
tests
Symfony container/YAML lint
Doctrine mapping/schema validation
```

Используй реальные scripts из `composer.json` и локальных tools.

- Gating работает report-first.
- Исправления выполняются точечно по найденным фактам.
- Секреты и private keys хранятся вне репозитория.
- Generated folders `vendor`, `node_modules`, `var`, cache и logs не входят в анализ исходного кода.
- Описательные docblock сохраняются.
- Таблицы Doctrine используют database prefix компонента, если он задан профилем.

## 15. Готовность изменения

Изменение готово, когда:

- код выражает одну текущую модель;
- namespace и typed layers корректны;
- generic CRUD не продублирован вне Cruding;
- Entity остаётся внутри operation boundary;
- зависимости объявлены явно;
- Objecting system fields не продублированы локально;
- старые tokens и aliases удалены после обновления callers;
- Gating, PHPStan и tests проходят либо точные внешние блокеры перечислены;
- добавленные, изменённые и удалённые файлы перечислены отдельно;
- каждое удаление подтверждено текущим деревом.

## 16. Порядок работы Codex

1. Прочитай текущие инструкции и код.
2. Составь краткий inventory.
3. Определи целевую каноническую модель.
4. Обнови implementation, callers, configuration и tests.
5. Удали подтверждённые obsolete files.
6. Запусти доступные проверки.
7. Дай итоговый отчёт с командами и результатами.

Изменение считается полным, когда старое имя или модель удалены не только из Entity, но также из runtime, Doctrine, YAML, serializer, Form, DTO, template, fixture, test и локальной документации.


## 17. Порядок работы MCP server + memory-MCP

Каждый компонент должен иметь граф через MCP server + memory-MCP;
Графы нужно обновлять;
При создании или рбновлении графов учитывается \www\.cbmignore а также локальный .gitignore;
В паняти должен быть однин общий граф для всего \www\, в твкде отдельные графы приложений;

## Workspace Rules

- Treat `D:\PhpstormProjects\www` as an umbrella workspace with multiple independent projects.
- Before changing code, inspect the nearest `composer.json`, `package.json`, or existing project docs for the target subproject.
- Avoid touching `vendor/`, generated artifacts, and unrelated project trees unless the task explicitly requires it.
- Prefer project-local scripts and configs over ad hoc one-off commands.
- Keep secrets out of git-tracked files. Use Windows user env vars for runtime secrets.

## Cloudflare AI Gateway

- Use `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, and `CF_GATEWAY_ID` or `CF_AIG_GATEWAY_ID`.
- Use `cf-ai-verify` to verify auth and `cf-ai-test` for a smoke request.
- Prefer `curl.exe` from PowerShell when validating Cloudflare endpoints.
- Use `codex-cf-review -Scope Changed` as the default daily review path.
- Keep the policy layer in `.gating/` when you need scope, prompt, schema, or exit-code changes.

## Codex Usage

- Keep global Codex defaults in `C:\Users\Admin\.codex`.
- Keep workspace-specific guidance in `D:\PhpstormProjects\www\.codex`.
- If a subproject has its own `AGENTS.md`, it overrides these workspace norms for that subtree.

## Composer

prod composer.prod.json
dev composer.json

## App Runtime

prod \www\App\config\kernel\runtime_scope.prod.lock
dev \www\App\config\kernel\runtime_scope.prod.lock