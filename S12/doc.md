# Вариант №12. Сервис учебного плана

**Главный документ:** какие дисциплины, в каком семестре, сколько часов (теория / практика), форма отчетности (экзамен / зачет).

## Сущность: Curriculum (учебный план)

### Информация, требуемая для создания Curriculum

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|-------------|---------|
| `discipline_id` | ID дисциплины | Yes | Integer | > 0 | |
| `group_id` | ID группы | Yes | Integer | > 0 | |
| `semester_number` | Номер семестра | Yes | Integer | 1..8 | |
| `theory_hours` | Часы теории | Yes | Integer | ≥ 0 | |
| `practice_hours` | Часы практики | Yes | Integer | ≥ 0 | |
| `assessment_form` | Форма отчетности | Yes | Enum | `exam` / `credit` | |

**Unique constraint:**  
`(group_id, discipline_id, semester_number)` — одна дисциплина не может быть дважды у одной группы в одном семестре.

### Возвращаемые данные при успешном создании

| Parameter | Type |
|-----------|------|
| `id` | Integer |
| `discipline_id` | Integer |
| `group_id` | Integer |
| `semester_number` | Integer |
| `theory_hours` | Integer |
| `practice_hours` | Integer |
| `assessment_form` | Enum |
| `is_active` | Boolean |

## Изменение Curriculum по ID

### Входные параметры

| Parameter | Description | Required | Type | Constraint | Default |
|-----------|-------------|----------|------|-------------|---------|
| `id` | ID записи учебного плана | Yes | Integer | > 0 | |
| `theory_hours` | Часы теории | No | Integer | ≥ 0 | `NULL` |
| `practice_hours` | Часы практики | No | Integer | ≥ 0 | `NULL` |
| `assessment_form` | Форма отчетности | No | Enum | `exam` / `credit` | `NULL` |

> `discipline_id`, `group_id`, `semester_number` изменить нельзя.

### Возвращаемые данные

| Parameter | Type |
|-----------|------|
| `id` | Integer |
| `discipline_id` | Integer |
| `group_id` | Integer |
| `semester_number` | Integer |
| `theory_hours` | Integer |
| `practice_hours` | Integer |
| `assessment_form` | Enum |
| `is_active` | Boolean |


## Удаление Curriculum по ID

Возвращает `True`, если запись **деактивирована** (`is_active = False`), иначе `False`.  
Физического удаления из БД нет — используется «мягкое удаление».

## Получение Curriculum по ID

### Возвращаемые данные

| Parameter | Description | Type |
|-----------|-------------|------|
| `id` | ID записи | Integer |
| `discipline_name` | Название дисциплины | String |
| `group_name` | Наименование группы | String |
| `semester_number` | Номер семестра | Integer |
| `theory_hours` | Часы теории | Integer |
| `practice_hours` | Часы практики | Integer |
| `assessment_form` | Форма отчетности | Enum |
| `total_hours` | Теория + практика | Integer |
| `is_active` | Активна ли запись | Boolean |


## Получение списка Curriculum с фильтрацией

### Входные параметры фильтрации

| Parameter | Description | Type |
|-----------|-------------|------|
| `group_id` | ID группы | Integer |
| `discipline_id` | ID дисциплины | Integer |
| `semester_number` | Номер семестра | Integer |
| `assessment_form` | `exam` / `credit` | Enum |
| `theory_hours_min` | Мин. часов теории | Integer |
| `theory_hours_max` | Макс. часов теории | Integer |
| `practice_hours_min` | Мин. часов практики | Integer |
| `practice_hours_max` | Макс. часов практики | Integer |
| `is_active` | `true` / `false` | Boolean |
| `page` | Номер страницы | Integer |
| `page_size` | Размер страницы | Integer |

> По умолчанию возвращаются только активные записи.

### Выходные данные (список)

| Parameter | Type |
|-----------|------|
| `id` | Integer |
| `discipline_id` | Integer |
| `discipline_name` | String |
| `group_id` | Integer |
| `group_name` | String |
| `semester_number` | Integer |
| `theory_hours` | Integer |
| `practice_hours` | Integer |
| `assessment_form` | Enum |
| `total_hours` | Integer |
| `is_active` | Boolean |


## ER-диаграмма

