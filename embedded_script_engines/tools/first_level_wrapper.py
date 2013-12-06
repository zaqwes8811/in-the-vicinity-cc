# coding: utf-8
import re  # регулярные выражения

# std
import sys

# Third_party
from generator.cpp import utils

# App
from _units import extract_variable_declaration
from _units import make_header
from _units import make_source
import han
import _units_han


def write_source(file_name, code):
    f = open(file_name, 'w')
    f.write(('\r\n'.join(code))
            .replace('\r', '@')
            .replace('@', ''))
    f.close()


def main():
    header_file_name = '../v8/src/point.h'
    header_file_name = './test-data/real_test_file.h'
    source = utils.ReadFile(header_file_name)

    # zaqwes
    #vars_ = extract_variable_declaration(source, header_file_name)
    vars_ = _units_han.extract_variable_declaration(source)

    #if
    # Make V8 view
    impls = []
    declarations = []

    for elem in vars_:
        if elem.is_array():
            pass
        else:
            i, d = elem.make_scalar_getter()
            if d:
                impls.append((i, elem.get_wrapper_class_name()))
                declarations.append((d, elem.get_wrapper_class_name()))
            else:
                print i

    code = make_header(declarations, 'point.h')
    header_name = 'forge_v8_point.h'
    write_source(header_name, code)
    code = make_source(impls, header_name)

    # Итоговый исходник
    write_source('forge_v8_point.cc', code)


if __name__ == '__main__':
    main()


