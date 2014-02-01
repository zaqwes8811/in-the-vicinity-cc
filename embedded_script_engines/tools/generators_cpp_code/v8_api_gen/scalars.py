# coding: utf-8
__author__ = 'Igor'

# std
import sys

# App
from generators_cpp_code.v8_api_gen import name_mapper
import inner_reuse_local as util


# zaqwes
class ScalarVariableField(object):
    """
    About:
    """
    def is_array(self):
        """
        About:
            vector vec;
            int array[]
        """
        result = False
        if '[' in self.variable_node_.name or 'vector' in self.variable_node_.type.name:
            result = True

        return result

    def get_array_size(self):
        if self.is_array():
            return 0
        else:
            return None

    def __str__(self):
        return str(self.class_name_)

    def __init__(self, class_name, variable_node):
        #if not isinstance(variable_node, ast.VariableDeclaration):
        #    raise Exception("Only scalar field support support!")

        self.class_name_ = class_name
        self.variable_node_ = variable_node

        # Регистрируем типы
        self.V8_GETTER_RECODER_ = {'int': 'Integer',
                                   'uint': 'Integer',
                                   'uchar': 'Integer',
                                   'bool': 'Boolean'}
        self.V8_SETTER_RECODER_ = {'int': 'Int32',
                                   'uint': 'Int32',
                                   'uchar': 'Int32',
                                   'bool': 'Boolean'}

    def get_wrapper_class_name(self):
        return 'ForgeV8' + self.class_name_ + 's'

    def make_scalar_getter(self):
        """
        About:
        class Point {
            public:  // bad, but now be it
            int x;
        };

        Notes:
            static method is BAD!
        """
        field_type, field_name, class_name = (self.variable_node_.type.name,
                                              self.variable_node_.name,
                                              self.class_name_)

        if field_type not in self.V8_GETTER_RECODER_:
            return "// Map not found: " + field_type + ' - ' + field_name, None

        def make_getter_header(field_name_local):
            return 'V8ScalarGetter_' + field_name_local + '(\r\n' + \
                   '    v8::Local<v8::String> name,\r\n' + \
                   '    const v8::PropertyCallbackInfo<v8::Value>& info)'

        template = make_getter_header(field_name) + ' \r\n' + \
                   '  {\r\n' + \
                   '  Local<Object> self = info.Holder();\r\n' + \
                   '  Local<External> wrap = Local<External>::Cast(self->GetInternalField(0));\r\n' + \
                   '  void* ptr = wrap->Value();\r\n' + \
                   '  ' + field_type + ' value = static_cast<' + class_name + '*>(ptr)->' + field_name + ';\r\n' + \
                   '  info.GetReturnValue().Set(' + self.V8_GETTER_RECODER_[field_type] + '::New(value));\r\n' + \
                   '}'

        return template, make_getter_header(field_name) + ';\r\n'

    # BUGS!! Нужно тоже пропустить через регистратор!!
    def setter_name(self):
        return 'V8ScalarSetter_'+self.variable_node_.name

    def getter_name(self):
        return 'V8ScalarGetter_'+self.variable_node_.name

    def make_scalar_setter(self):
        def make_setter_header(field_name_local):
            return 'V8ScalarSetter_' + field_name_local + '(\r\n' + \
                   '        v8::Local<v8::String> property, v8::Local<v8::Value> value,\r\n' + \
                   '        const v8::PropertyCallbackInfo<void>& info)'

        field_type, field_name, class_name = (self.variable_node_.type.name,
                                              self.variable_node_.name,
                                              self.class_name_)

        if field_type not in self.V8_GETTER_RECODER_:
            return "Map not found", None

        template = make_setter_header(field_name)+' \r\n' + \
                   '  {\r\n' + \
                   '  Local<Object> self = info.Holder();\r\n' + \
                   '  Local<External> wrap = Local<External>::Cast(self->GetInternalField(0));\r\n' + \
                   '  void* ptr = wrap->Value();\r\n' + \
                   '  static_cast<' + class_name + '*>(ptr)->' + field_name + ' = value->' + self.V8_SETTER_RECODER_[
                       field_type] + 'Value();\r\n' + \
                   '}'

        return template, make_setter_header(field_name)


class ScalarBuilder(object):
    def do_scalar_getters_decl(dec_wrappers):
        def wrap_scalar_getters_header(impl_local):
            code_result = []
            for impl in impl_local:
                code_result.append('  static void ' + impl[0])
            return code_result
        impls = []
        declarations = []
        for elem in dec_wrappers:
            if not elem.is_array():
                i, d = elem.make_scalar_getter()
                if d:
                    impls.append((i, elem.get_wrapper_class_name()))
                    declarations.append((d, elem.get_wrapper_class_name()))
                else:
                    print i

        code = wrap_scalar_getters_header(declarations)
        return code


    def do_scalar_setter_decl(dec_wrappers):
        def wrap_scalar_setters_header(impl_local):
            code_result = []
            for impl in impl_local:
                code_result.append('  static void ' + impl[0]+';\n')
            return code_result

        # zaqwes
        impls = []
        declarations = []
        for elem in dec_wrappers:
            if not elem.is_array():
                i, d = elem.make_scalar_setter()
                if d:
                    impls.append((i, elem.get_wrapper_class_name()))
                    declarations.append((d, elem.get_wrapper_class_name()))
                else:
                    print i

        code = wrap_scalar_setters_header(declarations)
        return code


    def do_scalar_setter_impl(dec_wrappers, class_name):
        # zaqwes
        impls = []
        for elem in dec_wrappers:
            if not elem.is_array():
                impl, d = elem.make_scalar_setter()
                if d:
                    impls.append('void '+make_v8_class_name(class_name)+'::'+impl+'\n')
                else:
                    print impl

        return impls


    def make_v8_class_name(name):
        return name + 'V8'


    def do_scalar_getter_impl(dec_wrappers, class_name):
        # zaqwes
        impls = []
        for elem in dec_wrappers:
            if not elem.is_array():
                impl, d = elem.make_scalar_getter()
                if d:
                    impls.append('void '+make_v8_class_name(class_name)+'::'+impl+'\n')
                else:
                    print impl

        return impls


    def do_scalar_connecters(dec_wrappers):
        # zaqwes
        impls = []
        for elem in dec_wrappers:
            if not elem.is_array():
                g, s, n = elem.getter_name(), elem.setter_name(), elem.variable_node_.name
                impls.append('  result->SetAccessor(\n      String::New("'+n+'"),\n      '+g+', \n      '+s)

        return impls