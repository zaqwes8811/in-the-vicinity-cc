/**
  file : Top.h

  feat. : удобно для небольших проектов

  con. : #include "Top.h"
*/
#include <iostream>
//#include "matrixFirst.h"
//#include <unistd.h>
//#include <stdio.h>
//#include <signal.h>
//#include <time.h>
//#include <sys/time.h>
/// ///



/**
  !! Укажем, что может содержать заголовочный файл:
    Определения типов                struct point { int x, y; };
    Шаблоны типов                    template<class T>
                                          class V { /* ... * / }
    Описания функций                 extern int strlen(const char*);
    Определения                      inline char get() { return *p++; }
    функций-подстановок
    Описания данных                  extern int a;
    Определения констант             const float pi = 3.141593;
    Перечисления                     enum bool { false, true };
    Описания имен                    class Matrix;
    Команды включения файлов         #include <signal.h>
    Макроопределения                 #define Case break;case
    Комментарии                      /* проверка на конец файла * / 
  !! С другой стороны, в заголовочном файле никогда не должно быть:
    Определений обычных функций    char get() { return *p++; }
    Определений данных             int a;
    Определений составных констант const tb[i] = { /* ... * / };

    !! Проще всего разбить программу на несколько файлов следующим образом: поместить определения
  всех функций и данных в некоторое число входных файлов, а все типы, необходимые для связи между
  ними, описать в единственном заголовочном файле

    !! Предостережение: обычно можно управиться с множеством, состоящим примерно из 10
  заголовочных файлов (плюс стандартные заголовочные файлы). Если же вы будете разбивать
  программу на минимальные логические единицы с заголовочными файлами (например, создавая для
  каждой структуры свой заголовочный файл), то можете очень легко получить неуправляемое множество
  из сотен заголовочных файлов.
*/
