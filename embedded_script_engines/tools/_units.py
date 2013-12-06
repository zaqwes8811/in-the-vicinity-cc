# coding: utf-8

# Third_party
from generator.cpp import ast


class ScalarVariableField(object):
    """
    About:
    """

    def __init__(self, class_name, variable_node):
        #if not isinstance(variable_node, ast.VariableDeclaration):
        #    raise Exception("Only scalar field support support!")

        self.class_name_ = class_name
        self.variable_node_ = variable_node

        # Регистрируем типы
        self.V8_GETTER_RECODER_ = {'int': 'Integer', 'std::string': 'String'}
        self.V8_SETTER_RECODER_ = {'int': 'Int32', 'std::string': 'String'}

    def get_wrapper_class_name(self):
        return 'V8'+self.class_name_

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
            return 'void v8_getter_' + field_name_local + '(\r\n' + \
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

        return template, make_getter_header(field_name)+';\r\n'

    def make_scalar_setter(self):
        field_type, field_name, class_name = (self.variable_node_.type.name,
                                              self.variable_node_.name,
                                              self.class_name_)

        if field_type not in self.V8_GETTER_RECODER_:
            return "Map not found"

        template = 'void v8_setter_' + field_name + '(\r\n' + \
                   '        Local<String> property, Local<Value> value,\r\n' + \
                   '        const PropertyCallbackInfo<void>& info) \r\n' + \
                   '  {\r\n' + \
                   '  Local<Object> self = info.Holder();\r\n' + \
                   '  Local<External> wrap = Local<External>::Cast(self->GetInternalField(0));\r\n' + \
                   '  void* ptr = wrap->Value();\r\n' + \
                   '  static_cast<' + class_name + '*>(ptr)->' + field_name + ' = value->' + self.V8_SETTER_RECODER_[
                       field_type] + 'Value();\r\n' + \
                   '}'

        return template


def extract_variable_declaration(source, header_file_name):
    """
    Abstract:
        Extract variable declaration form C++ header file.
    Args:
        source - content header file
        header_file_name - name header file

    Returns:
        [VarField0, ...]
    """
    builder = ast.BuilderFromSource(source, header_file_name)
    try:
        for node in builder.Generate():
            if isinstance(node, ast.Class):
                for record in node.body:
                    if isinstance(record, ast.VariableDeclaration):
                        # модификаторы и... *, & отделены от имени типа!
                        #if scalar?:
                        #elif  vector? std::vector<string>, Vector, List, Array...
                        # это не скаляр и сеттер будет другим https://developers.google.com/v8/embed
                        #else
                        #check what happened
                        yield ScalarVariableField(node.name, record)
    except KeyboardInterrupt:
        return
    except Exception as e:
        pass
