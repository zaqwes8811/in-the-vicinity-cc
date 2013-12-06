# coding: utf-8

# std
import re

# ПЕЧАТАТЬ ЛИ МАССИВЫ?????
# 0 - нет
# 1 - да
check_array_print = 0


class VarDeclaration(object):
    class Type(object):
        def __init__(self, type_name):
            self.name = type_name

    def __init__(self, type_name, name):
        self.type = VarDeclaration.Type(type_name)
        self.name = name


print("\n")
"""
var Point = function() {
}

var pointInstance = new Point();
"""


def removeComments(transmittingCode):
    deletingString = ""
    regular = re.compile('\/\/.*')
    searchResult = regular.search(transmittingCode)
    if searchResult:
        deletingString = searchResult.group()
        #print searchResult.group()
    return transmittingCode.replace(deletingString, "")


def delete_double_spaces(transmittedString):
    return transmittedString.replace("  ", " ")

# возвращает строку, в которой содержится все пары тип + имя переменной
def extract_var_declaration(class_transmit_code_):
    result = ""
    for i in class_transmit_code_.split('\n'):
        if '(' not in i and ")" not in i and "{" not in i and "}" not in i \
            and "#" not in i \
            and "public:" not in i \
            and "private" not in i \
            and "protected" not in i \
            and "using" not in i:
            p = re.compile("bool""|int""|vector<""|string""|char")
            m = p.search(i)
            if m:
                i = removeComments(i)
                i = delete_double_spaces(i)
                result = result + i + '\n'

    print result
    return getTypeAndVarList(result)


def PreparingToGetTypeAndVarList(transmittingString):
    transmittingString = transmittingString.replace('\t', " ") \
        .replace(';', "") \
        .replace('\n\t', " ") \
        .replace("  ", " ") \
        .replace('\n', " ")
    transmittingString = transmittingString.replace("  ", " ")
    return transmittingString


def getTypeAndVarList(declaration_string):
    folded_string = PreparingToGetTypeAndVarList(declaration_string)

    folded_string = folded_string.rstrip().lstrip()
    declarations = folded_string.split(' ')

    result = []
    var_type = ""
    # Bug was here
    for index, record in enumerate(declarations):
        if record:
            if index % 2:
                var_name = record
                if var_type and var_name:
                    result.append((var_type, var_name))
            else:
                var_type = record
    # Bug was here
    return result


def transmitCTypeToV8(type, typeFunc):
    result = ""
    if typeFunc == "get":
        if type == "int" or type == "uint" \
            or type == "char" \
            or type == "uchar":
            result = "Integer"
    if typeFunc == "set":
        if type == "int" or type == "uint" \
            or type == "uchar" \
            or type == "char":
            result = "Int32"
    if type == "bool":
        result = "Boolean"
        #bad
        #if type == "string" or type == "std::string":
        #result == "v8::String"
    if "string" in type:
        result = "v8::String"
    return result


def transmitSignedUnsignedTypes(type):
    if type == "uchar":
        return "unsigned char"
    if type == "uint":
        return "unsigned int"
    return type


def getFuncName(name):
    nameCapitalized = name.capitalize()
    return name.replace("_", "").replace(name[0], nameCapitalized[0]);


def make_scalar_getter(type, name):
    result = \
        "\n" + "static void v8_get_" + get_fun_name_by_array_types(name)[0] + """(Local<String> name,
    const PropertyCallbackInfo<Value>& info) {
  Local<Object> self = info.Holder();
  Local<External> wrap = Local<External>::Cast(self->GetInternalField(0));
  void* ptr = wrap->Value();
  """ + transmitSignedUnsignedTypes(type) + " value = static_cast<Point*>(ptr)->" + name + ''';
  info.GetReturnValue().Set(''' + transmitCTypeToV8(type, "get") + """::New(value));
}
"""
    return clear_result(ArrayOrNotArray(result, name, type, "get"))


def make_scalar_setter(type, name):
    result = \
        "\n" + "static void v8_set_" + get_fun_name_by_array_types(name)[0] \
        + '''(Local<String> property, Local<Value> value,
    const PropertyCallbackInfo<void>& info) {
  Local<Object> self = info.Holder();
  Local<External> wrap = Local<External>::Cast(self->GetInternalField(0));
  void* ptr = wrap->Value();
  static_cast<''' + "DataBase" + "*>(ptr)->" + name + "= value->" + transmitCTypeToV8(type, "set") \
        + "Value();" + '''
}
'''
    return clear_result(ArrayOrNotArray(result, name, type, "set"))


def get_fun_name_by_array_types(name):
    result = name
    index = ""
    regular = re.compile('\[.*')
    searchResult = regular.search(result)
    if searchResult:
        result = result.replace(searchResult.group(), "")
        index = searchResult.group()
    return result, index.replace("[", "").replace("]", "")


def make_array_index_getter_sample(type, name):
    result = "static void v8_get_array_index_" + get_fun_name_by_array_types(name)[0] \
             + """(uint32_t index,	const PropertyCallbackInfo<Value>& info) {
  if (index < """ + get_fun_name_by_array_types(name)[1] + """) {
    v8::Local<v8::Object> self = info.Holder();
    Local<External> wrap = Local<External>::Cast(self->GetInternalField(0));
    void* ptr = wrap->Value();
    int* """ + "database" + """ = static_cast<int*>(ptr);
    info.GetReturnValue().Set( """ + "v8::Number::New(database[index])" + """);
  } else {
    info.GetReturnValue().Set(Undefined());
  }
}"""
    return result


def make_array_index_setter_sample(type, name):
    result = "static void v8_set_array_index_" + get_fun_name_by_array_types(name)[0] + """(
  uint32_t index,
  Local<Value> value,
  const PropertyCallbackInfo<Value>& info) {
}"""
    return result


def make_array_index_getter_func(type, name):
    if "[" in name:
        return make_array_index_getter_sample(type, name)
    return ""


def make_array_index_setter_func(type, name):
    if "[" in name:
        return make_array_index_setter_sample(type, name)
    else:
        return ""


def make_array_index_getter(type, name):
    return make_array_index_getter_func(type, name)


def make_array_index_setter(type, name):
    return make_array_index_setter_func(type, name)


def make_array_getter(type, name):
    result = "static void v8_get_array_" + get_fun_name_by_array_types(name)[0] + """(
      Local<String> name,
      const PropertyCallbackInfo<Value>& info) {
  Local<Object> self = info.Holder();
  Local<External> wrap = Local<External>::Cast(self->GetInternalField(0));
  void* ptr = wrap->Value();
  SmallBase* database = static_cast<SmallBase*>(ptr);
  Handle<ObjectTemplate> templ = Local<ObjectTemplate>::New(
    Isolate::GetCurrent(),
    var_array_blueprint_);
  Handle<Object> instance = templ->NewInstance();
  Handle<External> array_handle = External::New(database->""" + get_fun_name_by_array_types(name)[0] + """);
  instance->SetInternalField(0, array_handle);
  info.GetReturnValue().Set<v8::Object>(instance);
}"""
    if "[" in name:
        return result
    else:
        return ""


def clear_result(result):
    result = result.replace('\n ', '\n').replace("\n\n\n", "")
    result = result.replace('\n\n', '\n').replace('\n\n}', '\n}')
    result = result.replace("}\n", "}\n\n").replace("}\n\n}", "}\n}").replace("}\n\n\n", "}\n\n")
    return result


def make_getter_and_setter_add(type, name):
    # for scalars
    result = "  result->SetAccessor(String::New(\"" + name + "\"), v8_get_" + name + ", v8_set_" + name + ");"
    result = ArrayOrNotArray(result, name, type, "add")
    # for arrays
    if "[" in name:
        result = "\n" + """
  result->SetAccessor(String::New(\"""" + get_fun_name_by_array_types(name)[0] + "\"), v8_get_array_" + \
                 get_fun_name_by_array_types(name)[0] + """);
  result->SetIndexedPropertyHandler(v8_get_array_index_""" + get_fun_name_by_array_types(name)[
                     0] + ", v8_set_array_index_" + get_fun_name_by_array_types(name)[0] + ");"
    return result


def ArrayOrNotArray(result, name, type, typeFunc):
    if check_array_print == 0:
        if "[" not in name and "vector" not in type:
            return result
        else:
            return ""
    if check_array_print == 1:
        if "[" not in name and "vector" not in type:
            return result
        else:
            return result
    if typeFunc == "add":
        return "error: bad logic (in make_getter_and_setter_add) or " \
               + check_array_print + " != 0 or 1, default = 0"
    if typeFunc == "set":
        return "error: bad logic (in make_scalar_setter) or " \
               + check_array_print + " != 0 or 1, default = 0"
    if typeFunc == "get":
        return "error: bad logic (in make_scalar_getter) or " \
               + check_array_print + " != 0 or 1, default = 0"


# ВРЕМЕННЫЙ вывод, пока не зарегистрировали массивы!) очищенный от лишних пробелов и отформатированный!
# еще добавил формирование функции CreateBlueprint
def make_scalars_and_accessors_with_formating(type_and_var_list):
    result = """v8::Handle<v8::ObjectTemplate> CreateBlueprint(
      v8::Isolate* isolate) {
"""
    for elem in type_and_var_list:
        result = result + make_getter_and_setter_add(*elem) + "\n"

    result = result + """
}"""

    result = result.replace('\n\n', '\n')

    for elem in type_and_var_list:
        result = result + make_scalar_getter(*elem) + make_scalar_setter(*elem)

    result = result.replace('\n ', '\n')
    result = result.replace('\n\n', '\n').replace('\n\n}', '\n}')
    result = result.replace("}\n", "}\n\n").replace("\n\n\n", "\n\n")

    return result

# 0 - вывод без массивов!
# 1 - вывод с массивами (по умолчанию 0)
check_array_print = 0


def extract_variable_declaration(source):
    """
    Args:
        source - string with code
    """
    from _units import ScalarVariableField
    type_and_var_list = extract_var_declaration(source)
    result = []
    for var in type_and_var_list:
        result.append(ScalarVariableField('unknown', VarDeclaration(*var)))

    return result
