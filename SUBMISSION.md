# Field Shift KZ — submission pack, NASA Space Apps 2026

Проверено 14.11.2026. Это подготовка первоначальной подачи проекта на хакатон
2026 года для Local Event Almaty и последующего отбора в Global Judging.
Форма конкурса не отправлена. Копировать следует только английские блоки
соответствующих полей ниже, после заполнения пропусков и проверки редактора.

Версия продукта для текста: `main`,
`b2ced8892a3ba9472718262ebe24bc2a3e4c4a05`, после PR #2 и #3.
[PR #6](https://github.com/Stalker-a/field-shift-kz/pull/6) с полной потребностью
рисового чека на момент сверки **открыт, не слит**. Его 1720 мм и новые проценты
пригодности не описаны как уже доступная функция. Проверены README, TZ.md,
SOURCES.md, `nasa_power.py`, `climate.py`, `crops.py`, `rotation.py`, `app.py`,
`ui_helpers.py`, requirements.txt и обсуждения [#4][I4]/[#5][I5]. AGENTS.md не найден.

## Проверенные официальные источники

Все документы ниже относятся к 2026 году. Открыты сами страницы через браузер;
поисковые сниппеты и правила прежних лет не использованы как подтверждение.

| Код | Документ, дата | Проверенные разделы |
|---|---|---|
| G | [Project Submission Guide][G], 13.11.2026 | Project Submission Start & End Times; Editing Your Project Submission Page; Project Page Form Field Instructions; Tips for Creating a Project Demo; Submitting Your Project |
| F | [Participant FAQs][F], 13.11.2026 | Navigating Your Hackathon Journey: What are the challenges?; How do teams submit their project?; What is Super Intelligence?; team requirements |
| J | [Judging & Awards Guide][J], 13.11.2026 | Eligibility for Global Judging; Judging Criteria; Phases 1–3 |
| L | [2026 Participant Terms and Conditions][L], обновлены 07.08.2026 | Submissions; Intellectual Property Rights in Solutions; Use of Third-Party Materials; Media Release |
| A | [Almaty 2026][A], дата обновления не указана | Local Event Schedule → Sunday, November 15; Details → Detailed Event Program; How to Participate |
| T | [DDT, публичная страница команды][T], дата обновления не указана | About/Team Information, Members, Project: Almaty, Kazakhstan; выбран Field Shift: Adapting Farms with NASA Data |
| C | [Ответ GO Team, Discussion #1916][C], 10.11.2026 | Срок и часовой пояс; уточнён по более подробному G, включая исключение Universal Event |

Страница A помечена User-Generated Content: расписание опубликовано местным
организатором, не является общим сроком платформы. Найденная DDT совпадает по
названию, challenge, событию и числу участников (три); владельцу следует подтвердить,
что это именно наша регистрация. Подтверждённость/не-waitlist всех участников
редактором не проверена.

Ограничения доступа: обычный веб-инструмент возвращал 502/тайм-ауты, локальное
HTTPS-чтение сайта — ошибку доверия сертификату. Защита не отключалась; браузер
успешно открыл G/F/J/L/A/T. Авторизованной сессии участника нет: публичный Project
DDT показывает заглушку, кнопки Edit нет, доступен Login. Частный черновик, required-
флаги, счётчики и валидатор живой формы **не проверены**. Пароль не запрашивался.
Один скриншот редактора внутри G содержит дату 2025 года: это иллюстрация,
а не доказательство лимитов формы 2026. Два других изображения не скачались.

## Срок и местное время

По G, **Project Submission Start & End Times / Submitting Your Project**:
подача открывается 14.11.2026 в 09:00 и закрывается **15.11.2026 в 23:59
по часовому поясу Local Event команды**. Для Universal Event отдельно действует
местное время проживания Team Owner. Нужно именно нажать Submit for Judging:
Save Progress не заменяет подачу.

Для указанного на странице DDT события Almaty:

| Событие | Asia/Almaty = Asia/Qyzylorda, UTC+5 | UTC | Смена даты |
|---|---|---|---|
| Открытие формы | 14.11.2026 09:00 | 14.11.2026 04:00 | Нет |
| Начало местных презентаций и оценки, A/Schedule | 15.11.2026 14:00 | 15.11.2026 09:00 | Нет |
| Подготовка текста по issue #4 | 15.11.2026 15:00 | 15.11.2026 10:00 | Нет |
| Заморозка кода TZ.md; материалы по issue #5 | 15.11.2026 18:00 | 15.11.2026 13:00 | Нет |
| Внутренняя отправка по TZ.md | До 15.11.2026 21:00 | До 15.11.2026 16:00 | Нет |
| Официальное закрытие онлайн-подачи | **15.11.2026 23:59** | **15.11.2026 18:59** | **Нет** |

Преобразование проверено `datetime`/`zoneinfo` для обеих зон на эти даты:
смещение +05:00. Неверное чтение «23:59 UTC» дало бы **16 ноября 04:59**
в Кызылорде — на пять часов позже фактического срока; это не разрешённое продление.

До общего закрытия заморозка в 18:00 оставляет 5 ч 59 мин, отправка до 21:00 —
2 ч 59 мин. Однако локальные презентации начинаются в 14:00: подготовка текста
к 15:00 и материалов к 18:00 может быть слишком поздней для местного показа.
Нужен готовый вариант до местной сессии или другого подтверждённого слота DDT.
14:00 — начало презентаций, **не подтверждённый отдельный срок закрытия формы**.
Точный слот, правила для virtual-участников Almaty и локальный срок загрузки
материалов должен подтвердить Local Lead (контакт опубликован на A).
Details указывает награждение 17:00–18:00, Schedule — начало в 18:00;
это расхождение не устранено догадкой. Отдельная местная регистрация через
Google Form на A обозначена обязательной; её выполнение DDT не проверено.

Срок 23:59 относится к первоначальной подаче, не к новым материалам финалистов.
J различает Phase 1 (локальный/Universal отбор, Global Nominees — 03.12.2026),
Phase 2 (Global Finalists/Honorable Mentions — 17.12.2026) и Phase 3
(Global Winners — 26.01.2027). Эти даты — объявления результатов,
не дополнительные дедлайны подачи. Отдельная последующая форма в источниках
не подтверждена. Внутренний финальный production-check issue #4 после 18:00
этим исследованием не заменяется.

Уведомления опубликованы до завершения документа:

- [Первое сообщение о часовом поясе][D1]; [уточнение по самому Guide][D2].
- [Срочное предупреждение о 14:00 и плане TZ.md][D3].
- [Лимиты demo для @Anayatqwp][M1]; [местное время показа в issue #5][M2].
- [Найденная DDT, вопросы о ранней работе, лицензии и редакторе][D4].

## Поля и ограничения

«Не подтверждено» не означает «необязательно» или «без ограничения».
G перечисляет восемь полей ниже, но не публикует числовые лимиты текста
и не отмечает required-флаг каждого текстового поля. Они должны быть сверены
в редакторе вошедшим участником; ограничения прежних лет не подставлены.

| Фактическое поле / действие | Обязательность | Проверенный лимит / условие | Источник и раздел |
|---|---|---|---|
| Project Name | Поле есть; отдельный required-флаг не проверен | Лимит символов/слов не опубликован в G | G, Project Page Form Field Instructions |
| High-Level Project Summary | Поле есть; required-флаг не проверен | Лимит и способ подсчёта не подтверждены | G, тот же раздел |
| Link to Project Demo | Demo обязательно для всех команд | Видео **≤30 секунд ИЛИ ≤7 слайдов**, включая титульный и вводные; публичная ссылка | G, Tips for Creating a Project Demo; J, Eligibility |
| Link to Final Project | Поле есть; required-флаг не проверен | Публичная ссылка без пароля/входа/разрешения; числовой лимит URL не указан | G, Form Field Instructions |
| Detailed Project Description | Поле есть; required-флаг не проверен | Лимит и способ подсчёта не подтверждены; инструменты входят сюда | G, Form Field Instructions |
| Use of Super Intelligence (SI) | Описание использования SI обязательно; тип/валидация контрола не проверены | Назвать где и как применяли инструменты; лимит не указан | G, Form Field Instructions → Use of SI; F, SI question |
| NASA Data | Для Global Award нужен хотя бы один NASA data/resource; UI required-флаг не проверен | Конкретные данные и способ использования; лимит не указан | G, Form Field Instructions → NASA Data |
| Space Agency Partner Data and Other References | Все использованные внешние ресурсы необходимо указать; UI required-флаг не проверен | Код, текст, изображения, данные, инструменты и лицензии; лимит не указан | G, Form Field Instructions; L, Use of Third-Party Materials |
| Terms and Conditions / original-work confirmations | Обязательные подтверждения владельца перед подачей | Права и оригинальность подтверждать только после проверки; не текстовое поле для автоматической вставки | G, Submitting Your Project; J, Eligibility |
| Submit for Judging | Обязательно для подачи | До указанного срока; проверить баннер успешной подачи | G, Submitting Your Project |

Отдельных полей «Tools», «Code URL», «Presentation URL» и «Video URL» в G нет:
инструменты включены в Detailed Description/References, код — в References;
в Demo вставляется одна выбранная ссылка на видео **или** слайды, а не ссылка
на интерактивное приложение вместо требуемого демоматериала.

Прочие подтверждённые требования G/J/L:

- Форма и связанные материалы — английские. Для речи видео на другом языке
  нужны английские субтитры; слайды должны быть английскими.
- Видео/документы размещают снаружи; на платформе их загрузка не поддерживается.
  Для изображений G указывает JPG/PNG/GIF до 10 MB. Ссылки нужно проверять
  без авторизации; превышение 30 секунд/7 слайдов исключает Global Judging.
- Слайды должны включать команду, имена участников и challenge. При этом L
  запрещает узнаваемые имена, голоса и изображения лиц до 18 лет в материалах;
  сведения и согласия проверяет владелец, возраст участников здесь не предполагается.
- SI/AI разрешены как помощь разработке; G запрещает использовать SI для
  придумывания самой идеи решения и менять/генерировать NASA branding.
  SI-изображения/видео требуют видимой маркировки, аудио — описания и метаданных,
  код/данные — признания SI-генерации в описании и метаданных. Нельзя утверждать,
  что отсутствие генерирующей модели в приложении означает отсутствие SI при разработке.
  Сам ответ на SI-вопрос, по G, не показывают жюри; маркировки в материалах видны.
- J требует одну официальную задачу, регистрацию всех членов команды в одном
  событии без waitlist и состав на Members. Локальная команда: 1–6 человек;
  Universal: 2–6. Оценка: Impact, Creativity, Validity, Relevance, Presentation.
- L требует права/лицензии на внешние материалы и полные ссылки. В main нет
  LICENSE: нельзя писать, что репозиторий уже лицензирован как open source.
  Условия описывают распространение NASA под Apache 2.0 при отсутствии указанной
  OSI-лицензии; это не добавляет LICENSE в репозиторий. Решение остаётся владельцу.

## Английский текст для полей

Блоки ниже описывают проверенный `main`. После нового слияния сверить их повторно.
Служебные подписи, счётчики, комментарии и русские пояснения в форму не копировать.

### Project Name

<!-- field:project_name -->
```text
Field Shift KZ
```
<!-- /field -->

### High-Level Project Summary

<!-- field:summary -->
```text
Field Shift KZ helps farmers in Kazakhstan explore crop rotations as growing conditions change. Using NASA POWER daily data from 1981 to 2025, it compares recent seasonal temperature, rainfall and root-zone wetness with an earlier baseline. Farmers choose a location, soil type, irrigation setting and priorities, then compare 16 crops and up to three four-year rotation options. Each option is compared with the farmer's current rotation and explained through transparent prototype scores. A 2035 view extends the observed trend rather than predicting climate. The tool supports discussion with local agronomists; it does not establish future yield, income or measured water savings.
```
<!-- /field -->

### Link to Project Demo

**НЕ ЗАПОЛНЕНО.** В issue #5 нет опубликованной ссылки автора на слайды или
видео. Вставить одну актуальную публичную ссылку от @Anayatqwp на ≤30 секунд
видео **или** ≤7 слайдов. Проверить весь материал, длительность/число слайдов,
английский язык/субтитры, права и SI-маркировки. Пропуск не отправлять в форму.

<!-- field:demo -->
```text
TO BE FILLED: one publicly accessible URL to the final video (30 seconds maximum) OR slide deck (seven slides maximum, including title and introduction).
```
<!-- /field -->

### Link to Final Project

<!-- field:final_project -->
```text
https://stalker-a-field-shift-kz-app-xokyoc.streamlit.app/
```
<!-- /field -->

### Detailed Project Description

<!-- field:description -->
```text
Field Shift KZ is a working decision-support prototype for Kazakhstan, developed by team DDT for the Field Shift: Adapting Farms with NASA Data challenge. It connects NASA climate history with explicit crop assumptions and the farmer's priorities so that alternative rotations can be explored and questioned.

A farmer selects one of 12 demo regions, enters coordinates, or previews a point on a map before applying it. The farmer then chooses a soil class, irrigation setting, priorities and current four-year rotation. The app compares April-September conditions in 1981-2000 with 2006-2025 and displays temperature, rainfall, root-zone wetness, reference evaporative demand, water deficit, frost-free season, last spring frost, hot days and dry spells. The 2035 view extends the observed historical trend; it is not a climate-model projection or a weather forecast.

The crop view scores 16 crops using temperature, available water, frost-free days and a heuristic salinity factor. Rotation search filters four-year sequences through crop-family and repetition rules. It offers three distinct options when suitable options exist, scores them for soil health, water saving, relative income and resilience, and compares them with the farmer's current rotation. The default reference is wheat, wheat, wheat and green fallow. Explanations and a downloadable field summary keep the selected location, soil, irrigation and priorities attached to the result.

NASA POWER supplies the environmental inputs. FAO references and Kazakhstani agronomic publications inform the crop-parameter audit, with unsupported values and mismatched definitions explicitly recorded. Soil storage, irrigation amounts and several crop ratings remain prototype assumptions. The present public version uses nominal crop evapotranspiration for rice and does not yet account for the complete flooded-paddy water requirement, so rice water-fit results need particular caution.

The implementation uses Python, Streamlit, pandas, NumPy, Plotly, Requests, Folium and streamlit-folium. OpenStreetMap provides the basemap. Derived monthly and yearly tables for the 12 demo points are included in the repository, allowing those analyses without a new NASA download. First-time custom points need NASA access, and map tiles need an internet connection. The app is hosted on Streamlit Community Cloud. OpenAI Codex assisted code, tests, source review and documentation; the app itself uses deterministic calculations rather than LLM inference.

The intended benefit is a clearer, reproducible conversation about climate adaptation and crop choices. Scores are relative model indicators, not proven yield, monetary profit, measured water savings or validated soil improvements. Gridded NASA data do not measure an individual field; seasonal aggregation and approximate agronomy limit interpretation. Local soil measurements, crop calendars and agronomist-led validation are needed before farm decisions. Future work includes better field-specific inputs and evaluation with local users. These are development goals, not completed features.
```
<!-- /field -->

### Use of Super Intelligence (SI)

Это **подтверждённая часть раскрытия**, не утверждение о полном перечне всей
команды. Другие инструменты, использование SI при выборе идеи, слайдах, изображениях,
голосе и видео запрошены в [issue #4][D1] и [issue #5][M1]. Перед вставкой владелец
должен дополнить этот блок фактическими сведениями. Не писать «AI was not used».

<!-- field:si -->
```text
OpenAI Codex was used as a coding and writing assistant for interface implementation, tests, agronomic-source review and documentation, including this submission draft. It generated or revised code and prose. AI-assisted changes are recorded in the repository and pull requests, and automated checks have been run. NASA POWER values are retrieved from the public API rather than generated by AI. The running application uses deterministic calculations and does not call an LLM. This statement covers the verified coding-assistant work; the team must complete the record of any additional SI tools or generated media before submission.
```
<!-- /field -->

### NASA Data

<!-- field:nasa_data -->
```text
NASA POWER (Prediction Of Worldwide Energy Resources) is the app's environmental data source. We use its daily point API, community AG, for 1 January 1981 through 31 December 2025. Five parameters are requested: T2M (daily mean air temperature at 2 m, degrees Celsius), T2M_MAX (daily maximum temperature), T2M_MIN (daily minimum temperature), PRECTOTCORR (bias-corrected precipitation, mm/day), and GWETROOT (root-zone soil wetness, dimensionless 0-1).

T2M, PRECTOTCORR and GWETROOT describe seasonal conditions and their historical change. T2M_MIN identifies frost timing and frost-free days; T2M_MAX identifies hot days. The temperature series also support Hargreaves reference evapotranspiration, which is compared with rain to describe water deficit. Rainfall identifies dry spells. Seasonal temperature, precipitation, root-zone wetness and frost-free days enter crop-fit and rotation scoring. The other indicators provide context in the climate dashboard.

The app aggregates the daily inputs into monthly and yearly tables and includes derived caches for 12 Kazakhstan demo points. Recent conditions are 2006-2025, compared with 1981-2000; the main season is April-September. The 2035 scenario is a linear extension of the historical trend, not NASA forecast data. Crop and soil parameters are separate assumptions, not NASA measurements.

NASA POWER: https://power.larc.nasa.gov/
API documentation: https://power.larc.nasa.gov/docs/services/api/
Daily point endpoint used by the code: https://power.larc.nasa.gov/api/temporal/daily/point
```
<!-- /field -->

### Space Agency Partner Data and Other References

<!-- field:references -->
```text
No additional Space Agency Partner dataset is used by the current implementation.

Agronomic references:
- C. Brouwer and M. Heibloem, FAO Irrigation Water Management, Training Manual No. 3: Irrigation Water Needs (1986), Part II, chapter 3, tables 6 and 14, and chapter 4, section 4.4. Crop water needs are approximate seasonal ETc, distinct from irrigation application and full paddy demand.
https://www.fao.org/4/s2022e/s2022e07.htm
https://www.fao.org/4/s2022e/s2022e08.htm
- R. G. Allen, L. S. Pereira, D. Raes and M. Smith, Crop Evapotranspiration, FAO Irrigation and Drainage Paper 56 (1998): Hargreaves reference evapotranspiration, crop stages and soil-water accounting.
https://www.fao.org/4/x0490e/x0490e00.htm
- R. S. Ayers and D. W. Westcot, Water Quality for Agriculture, FAO Irrigation and Drainage Paper 29 Rev. 1 (1985), chapter 2, tables 4-5. Published salinity thresholds were reviewed; they were not converted into the prototype's 0-1 salt-tolerance scores.
https://www.fao.org/4/t0234e/t0234e03.htm
- FAO ECOCROP species records were reviewed for temperature ranges and crop cycles. They do not directly validate April-September mean-temperature thresholds in Kazakhstan.
https://www.fao.org/geospatial/data-and-tools/data-portals/ecocrop/
- Kazakhstan Ministry of Agriculture/NASEC catalogue of domestic crop varieties and publications from the A. I. Barayev Research and Production Centre for Grain Farming were reviewed for local crop forms and calendars. Their original-language references, individual crop records and evidence limitations are preserved in the repository's source audit; not all local growth periods match sowing-to-harvest definitions.
https://github.com/Stalker-a/field-shift-kz/blob/main/SOURCES.md

Software and services:
Python; Streamlit (https://streamlit.io/); pandas (https://pandas.pydata.org/); NumPy (https://numpy.org/); Plotly (https://plotly.com/python/); Requests (https://requests.readthedocs.io/); Folium (https://python-visualization.github.io/folium/); streamlit-folium (https://github.com/randyzwitch/streamlit-folium). Direct dependency versions are pinned in requirements.txt. Streamlit Community Cloud hosts the app. Git/GitHub provide version control. OpenStreetMap contributors provide the map tiles; map attribution is retained (https://www.openstreetmap.org/copyright). OpenAI Codex assisted code and documentation as described in the SI disclosure. Dataset and software licenses remain those of their respective providers; the team must verify the final rights and license documentation before the form's declarations.

Project code: https://github.com/Stalker-a/field-shift-kz
Live application: https://stalker-a-field-shift-kz-app-xokyoc.streamlit.app/
```
<!-- /field -->

## Подсчёт длины

Числовые лимиты текстовых полей и правила счётчика живой формы не подтверждены.
Поэтому ниже **справочные фактические размеры**, а не сертификат соответствия
неизвестному лимиту. Считается только содержимое каждого блока `text`, без
ограждений, подписей и завершающего перевода строки. Символы включают пробелы,
пунктуацию, URL и внутренние переводы строк LF (один символ); слова — токены,
разделённые whitespace. Английские блоки ASCII: Unicode- и UTF-16-длины совпадают.
WYSIWYG/HTML-разметка редактора может считаться иначе. После вставки надо сверить
счётчик/ошибки формы; не применять лимиты предыдущих лет.

<!-- counts:start -->
| Поле | Символов | Whitespace-слов | Статус лимита |
|---|---:|---:|---|
| Project Name | 14 | 3 | Числовой лимит формы не подтверждён |
| High-Level Project Summary | 684 | 101 | Числовой лимит формы не подтверждён |
| Link to Project Demo (пропуск) | 153 | 24 | Материал отсутствует; размер пропуска не подтверждает соблюдение 30 секунд/7 слайдов |
| Link to Final Project | 58 | 1 | Числовой лимит формы не подтверждён |
| Detailed Project Description | 3102 | 431 | Числовой лимит формы не подтверждён |
| Use of Super Intelligence (SI), подтверждённая часть | 634 | 94 | Числовой лимит формы не подтверждён |
| NASA Data | 1547 | 198 | Числовой лимит формы не подтверждён |
| Space Agency Partner Data and Other References | 2725 | 302 | Числовой лимит формы не подтверждён |
<!-- counts:end -->

Для Demo ограничение относится к самому медиаматериалу, не к длине URL.
Длительность видео/количество слайдов пока не проверены: ссылок нет.

## Доступность ссылок и проверка состояния

| Ссылка / объект | Фактически проверено 14.11.2026 |
|---|---|
| [Live application][APP] | Анонимный браузер открыл работающий Field Shift KZ, данные Kostanay, кнопку выбора карты, параметры сценария, четыре вкладки и Download field summary; вход не нужен. Это проверка доступности, не финальный production-check после последнего merge. |
| [Code][CODE] | Публичный репозиторий склонирован в отдельную папку; main и исходники прочитаны; исходный HEAD b2ced889. |
| [DDT][T] | Публично доступны About/Members; Local Event Almaty; Project пока показывает заглушку. Сохранённый приватный черновик не виден. |
| G/F/J/L/A | Открыты и прочитаны браузером без входа; ссылки на разделы взяты из самих документов. |
| NASA POWER API docs; FAO Manual 3 §4.4; FAO-56 глава 6; FAO-29 глава 2 | Веб-инструмент открыл страницы первичных источников. Голый daily-point endpoint в поле NASA Data требует параметров запроса и не является кликабельным готовым набором данных. |
| Ссылки инструментов в References | Открыты Streamlit, pandas, NumPy, Plotly, Requests и OpenStreetMap copyright; Folium вернул страницу перенаправления на latest docs; README streamlit-folium доступен через GitHub. Это проверка адресов, не полный аудит лицензий зависимостей. |
| SOURCES.md и остальные агрономические ссылки | Сверены с source audit текущего main; это история его исследования, не новое подтверждение всех сортовых значений. Недоступность части PDF уже описана там. |
| Слайды @Anayatqwp | **Ссылка не опубликована в issue #5; доступ, язык и ≤7 слайдов не проверены.** |
| Видео @Anayatqwp | **Ссылка не опубликована в issue #5; доступ, субтитры и ≤30 секунд не проверены.** |
| Прямая страница challenge из поискового результата | Браузер вернул Page Not Found; название и смысл challenge подтверждены публичной страницей DDT. Дополнительные challenge-specific требования/список ресурсов по этой странице не подтверждены. |

SOURCES.md и TZ.md сейчас русские, часть исходных казахстанских публикаций тоже.
Английские блоки выше дают самостоятельное объяснение метода и ограничений;
не утверждается, что все материалы репозитория уже переведены. Требование
английского языка для связанных оцениваемых материалов нужно учесть до подачи;
для цитируемых первичных публикаций на другом языке уточнить трактовку у организатора.

AI/SI provenance metadata этого документа: OpenAI Codex assisted drafting,
source review and verification; NASA input data were not SI-generated.
Этот документ не подтверждает отсутствие других SI-инструментов команды.

## Что ещё нужно от команды

1. Одна финальная demo-ссылка из issue #5: ≤30 секунд видео или ≤7 слайдов;
   можно опубликовать оба материала, но выбрать основной для поля Demo.
   После получения открыть без авторизации и проверить весь материал.
2. Подтвердить DDT-регистрацию, не-waitlist состав, обязательную местную форму
   Almaty, слот/локальные требования до презентаций с 14:00. Для этого не нужен
   пароль в чате: редактор и подтверждения проверяет вошедший участник.
3. Снять required-флаги, лимиты, единицы счётчиков и формат SI-контрола с живой
   формы 2026; адаптировать только соответствующий английский блок и пересчитать.
4. Дополнить честное SI-раскрытие всей команды: инструменты и роли, включая
   происхождение идеи и медиаматериалов; проверить маркировки/метаданные и права.
5. Уточнить допустимость ранней подготовки: F запрещает начинать challenge до
   хакатона, а git содержит прототип `cbbf3b8` от 12.11 и правки 13.11.
   Это вопрос eligibility к Local Lead/GO Team, не доказанный здесь запрет участия.
   История сохранена; утверждения «всё создано только 14–15 ноября» в тексте нет.
6. Владелец должен решить вопрос лицензии оригинального кода и проверить
   лицензии/согласия внешних материалов и ограничения по лицам младше 18 лет.
   Нельзя автоматически подтвердить original work/rights за него.
7. Перед фактической отправкой повторить сверку main и production. Если PR #6
   будет объединён, заменить только устаревшую фразу о рисе в Detailed Description
   на описание опубликованного сценария по обновлённому SOURCES.md, пересчитать
   длину и переснять материалы. Нельзя заранее выдавать ветку PR за production.

Для этого PR меняется только SUBMISSION.md. Код, тесты, TZ.md и права доступа
не меняются. Проверки документа: соответствие восьми названиям полей G,
подсчёт всех блоков, точный перевод времени, отсутствие неподтверждённых обещаний,
доступность ключевых ссылок, повторная сверка main/issue #4/#5/PR #6 и
`git diff --check`. Программные тесты для изменения одного Markdown-файла
не запускались. Форма конкурса не заполнялась и не отправлялась.

[G]: https://www.spaceappschallenge.org/resources/project-submission-guide/
[F]: https://www.spaceappschallenge.org/resources/participant-faqs/
[J]: https://www.spaceappschallenge.org/resources/judging-awards-guide/
[L]: https://www.spaceappschallenge.org/legal/
[A]: https://www.spaceappschallenge.org/2026/local-events/almaty/
[T]: https://www.spaceappschallenge.org/2026/find-a-team/ddt/
[C]: https://github.com/nasa/spaceapps/discussions/1916
[I4]: https://github.com/Stalker-a/field-shift-kz/issues/4
[I5]: https://github.com/Stalker-a/field-shift-kz/issues/5
[APP]: https://stalker-a-field-shift-kz-app-xokyoc.streamlit.app/
[CODE]: https://github.com/Stalker-a/field-shift-kz
[D1]: https://github.com/Stalker-a/field-shift-kz/issues/4#issuecomment-6873537769
[D2]: https://github.com/Stalker-a/field-shift-kz/issues/4#issuecomment-6873564425
[D3]: https://github.com/Stalker-a/field-shift-kz/issues/4#issuecomment-6873579057
[D4]: https://github.com/Stalker-a/field-shift-kz/issues/4#issuecomment-6873637635
[M1]: https://github.com/Stalker-a/field-shift-kz/issues/5#issuecomment-6873564223
[M2]: https://github.com/Stalker-a/field-shift-kz/issues/5#issuecomment-6873579304
