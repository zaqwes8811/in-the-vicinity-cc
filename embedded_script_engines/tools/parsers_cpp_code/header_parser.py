# coding: utf-8

# std
import re

# App
from generators_cpp_code.v8_api_gen import scalars
import utils_local


class VarDeclaration(object):
    class Type(object):
        def __init__(self, type_name):
            self.name = type_name

    def __init__(self, type_name, name):
        self.type = VarDeclaration.Type(type_name)
        self.name = name


class HeaderParserHandmade(object):
    def first_filtration(self, code_lines):
        """ Возвращает строку, в которой содержится все пары тип + имя переменной

        class {
            // Work
            Type var;
            Type function(Type var);
            Type var[SOME];

            Type function(
                Type0 var);

            // Don't work
            Type<Type<
                Var> var;
            Type function(
                Type1 var,
                Type0 var);

            // May be not work
            Type function() {

            }
        }
        """
        result = []
        filter_regex = "bool""|int""|vector<""|string""|char"

        for line in code_lines:
            # Фильтрация кода
            # Может негенерить много ошибок
            # Можно внутри класса разбить так.
            # Сперва вытянуть в строку.
            # Затем разбить ;/:/ и только потом отфильтровать.
            if '(' not in line \
                    and ")" not in line \
                    and ";" in line \
                    and "{" not in line \
                    and "}" not in line \
                    and "#" not in line \
                    and "public:" not in line \
                    and "private" not in line \
                    and "protected" not in line \
                    and "using" not in line:
                pattern = re.compile(filter_regex)
                search_result = pattern.search(line)
                if search_result:
                    line_copy = line
                    line_copy = line_copy.lstrip().rstrip()
                    line_copy = utils_local.remove_cc_comments(line_copy)
                    line_copy = utils_local.delete_double_spaces(line_copy)
                    result.append(line_copy)

        return '\n'.join(result)

    def extract_var_declaration(self, source):
        code_lines = source.split('\n')
        declaration_string = self.first_filtration(code_lines)

        # Похоже вся магия здесь
        folded_string = self.end_filtration(declaration_string)

        # Похоже на итоговую запаковку
        type_name_list = self.make_type_value_list(folded_string)
        return type_name_list

    def remove_lr_spaces(string):
        return string.rstrip().lstrip()

    def make_type_value_list(self, folded_string):
        folded_string = self.remove_lr_spaces(folded_string)

        intermediate = []
        for at in folded_string.split(';'):
            pair = self.remove_lr_spaces(at)
            if not ('*' in pair or '=' in pair or 'const' in pair or 'static' in pair or pair.count('[') > 1):
                intermediate.append(pair)

        declarations = ' '.join(intermediate).split(' ')

        result = []
        var_type = ""
        # Bug was here
        for index, record in enumerate(declarations):
            record = self.remove_lr_spaces(record)  # Да, эти лучше тоже отфильтровать
            if record:
                if index % 2:
                    var_name = record
                    if var_type and var_name:
                        result.append((var_type, var_name))
                else:
                    var_type = record
                    # Bug was here
        return result

    def end_filtration(self, declaration_string):
        declaration_string = declaration_string\
            .replace('\t', " ") \
            .replace('\n\t', " ") \
            .replace("  ", " ") \
            .replace('\n', " ")
        declaration_string = utils_local.delete_double_spaces(declaration_string)
        return declaration_string

    def extract_variable_declaration_own(self, source, class_name='unknown'):
        """
        Args:
            source - string with code
        """
        type_and_var_list = self.extract_var_declaration(source)
        result = []
        for var in type_and_var_list:
            result.append(scalars.ScalarVariableField(class_name, VarDeclaration(*var)))

        return result