# TODO: в описании указать, что мы используем ленивую подгрузку. В будущем добавить Django Style поиски через "__"

| Стиль      | Можно фильтровать по связанной модели? | Какой синтаксис?        | Когда нужен?             |
| ---------- | -------------------------------------- | ----------------------- | ------------------------ |
| ORM-style  | Нет                                    | `User.is_active == ...` | Простые фильтры          |
| JOIN-style | Да                                     | `Order.user`, `User...` | Фильтры по связям        |
| Алиасы     | Да (и даже по нескольким связям)       | `aliased(User)`         | Self-join, сложные связи |
