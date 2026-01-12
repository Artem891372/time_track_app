create table if not exists tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_name           text,
    date_day         date,
    complite_sec       int,
    hour_week_limit    int,
    start_datetime      datetime,
    last_update     datetime
);