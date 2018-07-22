# dude
Примитивный интерпретатор чистого функционального ЯП без спецэффектов на python. Имеет вывод ошибок с указанием строки исходника и вероятной причины ошибки.

Является реализацией функционального языка, используемого как язык примеров и упражнений в книге С.М. Дудакова "Математическое введение в информатику" (Тверь, 2003). Там же можно найти более подробное описание синтаксиса и семантики языка.

# Синтаксис и семантика
Программа должна содержать главную функцию, которая описывается как
    Alg Name;
    arg arg1, arg2, ..., argn;
        // put your code here
    end;

Программа может содержать произвольное количество побочных функций с синтаксосом
    Sub Name;
    arg arg1, arg2, ..., argn;
        // put your code here
    end;

Можно использовать вызов главной или побочных функций вида `Name(arg1, arg2, ..., argn)`, вызовы можно использовать в выражениях.

В выражениях можно использовать общепринятые операторы арифметических действий `+`, `-`, `*`, `/`, `%`. Приоритет операторов общепринятый. Для изменения приоритета можно использовать скобки. Есть специальные выражения, которые являются тестами. Их синтаксис:
    <expression> < <expression>
или
    <expression> = <expression>

Результатом теста является 1 или 0 в зависимости от истинности или ложности теста соответственно.

Для вычисления выражений используется обычный алгоритм Дейкстры для преобразования в обратную польскую запись и вычисление на стеке.

Имеется две языковых конструкции, дающие Тьюринг-полную ситему: ветвление (условное выражение) и присваивание (возврат).

Ветвление:
    if <test> then
	foo = bar;
    [else
        spam = eggs;]
    end;
Ветвление может быть неполным.

Присваивание интуитивно понятно. Присваивать можно в переменные с любыми именами, все переменные считаются существующими, покуда хватает памяти. При использовании неинициализированной переменной, её значение полагается равным нулю.

Для каждой функции в программе существует переменная возврата, её имя совпадает с именем функции. Значение, содержащееся в этой переменной на момент выхода из функции считается возвращаемым значением.

Выполнение программ происходит прямо на AST.

# Использование

    $ ./dude.py program.dude arg1 arg2 ... argn

Первым аргументом интерпретатору передаётся файл с запускаемой программой, затем следуют значения стольких аргументов, сколько требуется передать главной функции программы, помеченной `Alg`.

# Примеры
В `demos/` есть примеры проргамм на языке, которые можно запустить интерпретатором.

`factorial.dude` классический рекурсивный факториал

`closest_prime.dude` вычисляет наименьшее простое число, не меньшее, чем переданный аргумент


# TODO
В данный момент для обхода абстрактно-синтаксического дерева используется подлинная рекурсия. В зависимости от алгоритма и величины значений аргументов можно получить maximum recursion depth exceeded. Можно этого избежать, разворачивая дерево в список и используя операторы перехода, то есть по сути преобразовывая любую функциональную программу в программу с метками, например, по теореме из той же книги С.М. Дудакова. 
