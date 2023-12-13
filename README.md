I want this game works in
    console on local comp
    on remote comp


Logic must be in the one place and generic for all platforms

User has opportunities to:
    specify the number of rows
    specify the length of win row


Interface:
    / method to start a game
    / method to get a board
    / method to make a move


Architecture:
    Layers:
        Repo - place for storing all info about game and moves

        Logic - All game logic locates here. Appropriate for all presentaions types

        Present - There are 2 types of presentations: API and
            console. Both of them must invoke functions of Logic layer


Create client in Golang



Простая реализация:

main - Вечный цикл, который просит сделать ход и после каждого хода
    переключает игрока. Также, после каждого хода запускается 
    проверка:
        1. на случай, если кто то выиграл, 
    
    Если никто не выиграл, то переключается игрок и цикл повторяется


make_move - получает номер клетки, номер игрока и выполняет проверку:
        1. либо, если клетка уже занята, 
        2. либо не существует
    если с проверками ок, то заполняет клетку


Номер игрока и его фишка хранится в базе



Взаимодействие с бэкендом:
    Браузер, Го клиент через сокеты


Слой логики должен быть общий

Repositories:

    POSTGRES
        users
            id: int
            name: string
            password_hash: string

        games
            game_id: int
            started_at: datetime
            users_ids: []integer
            finished_at: datetime
            winner: user_id

    REDIS
        current_games:
            users_ids: []integer
            chips: {user_id1: "X", user_id2: "Y"}
            next_move: user_id1
            board: JSON

        searching_partners:
            row_count: [user_id]integer


Logic:

    User init a game and we check Redis searching_partners. If list is not empty, we randonly get user_id and create a game in Redis current_games.

    Each user has ID so it is needed to make an auth logic

    Interfases:
        post "/auth"
            REQUEST: {
                username: str,
                password: str
            }
            RESPONSE: {
                token: str
            }

        post "/start-game
            REQUEST: {
                rows_count: int
            }
            HEADERS: {
                token: str
            }
            RESPONSE: {
                game_started: bool
                partner_id: int | None
                room_id: UUID | None
            }

            Когда игрок начинает новую игру, уходит пост запрос на бэк, там в редисе смотрим наличие ожидающего игрока с таким количеством клеток, если он есть, то возвращаем его айди и game_started=True и айди комнаты
            Если нет, то создаем в редисе новую запись и game_started=False

        post "/remove-from-expecting-list"
            REQUEST: {
                user_id: int
            }
            HEADERS: {
                token: str
            }
            RESPONSE: {
                status: ok
            }

        При отключении клиента, отправлять этот запрос


        ws "/game/{UUID}"
            REQUEST: {
                action: [move]
                row: int
                col: int
            }
            RESPONSE: {
                status: [victory, end, ok]
                winner: int | None
            }

        Первичная проверка хода реализована на клиенте. То есть, проверяется, что клетка свободна, также, очередь хода регулируется клиентом

        Когда игрок делает ход, на клиенте определяется позиция клетки, проставляется фишки и данные отправляются на бэк. 


Архитектура кода


Game - интерфейс управления игрой
- room_id: UUID
- repo: repo
- checkers
- board
- next_move: Player

- start()
Создается доска, игроки, чекер

- make_move(row: int, col: int, player_id) -> Event


Board - имплементация игровой доски.
чтобы каждый раз не лезть в редис и не парсить доску оттуда, в рантайме всегда хранится текущая позиция.
------------
|0|0|0|
|1|0|2|
|1|2|0|
------------
- current_position
- checker

- create_board(rows: int)
- make_move(row: int, col: int, player_id)


Checker - класс, реализующий все проверки
    Проверка выигрыша
    Проверка доступности хода
- check_win() - выдает бул и айди фигуры в случае победы
- check_move()
передается доска и клетки хода. Проверяется, есть ли такое поле и не занято ли оно

Repo - класс, инкапсулирующий логику хранилища данных
- set_board(board) 
- get_board() -> board


Authentication
    - check_token(token: str) -> user_id | Exception
    - create_user(username: str, password: str) -> user_id |    Exception
    - create_token(user_id) -> str

Точка доступа в игру:
    Вебсокет роут, запускающий хэндлер, в котором создаются все основные сущности


Начать с реализации логики, репозиториев
Обязательно тесты