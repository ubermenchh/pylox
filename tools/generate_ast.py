import sys 

def main():
    if len(sys.argv) > 2:
        print("Usage: python generate_ast.py <output directory>")
        sys.exit(1)

    output_dir = sys.argv[1]

    define_ast(
            output_dir,
            "Expr",
            [
                "Binary | left, operator, right",
                "Grouping | expression",
                "Literal | value",
                "Unary | operator, right"
                ]
            )


def define_ast(output_dir, base_name, types):
    path = output_dir + "/" + base_name + ".py"
    output_file = open(path, "w", encoding="UTF-8")
    

    define_imports(output_file)
    define_base_class(output_file, base_name)
    define_visitor(output_dir, base_name, types)

    # the AST classes 
    for type in types:
        class_name = type.split("|")[0].strip()
        fields = type.split("|")[1].strip()
        define_type(output_file, base_name, class_name, fields)

def define_base_class(output_file, base_name):
    output_file.write(f"class {base_name}:\n")
    output_file.write(f"    pass\n")

def define_imports(output_file):
    output_file.write("from abc import ABC, abstractmethod\n")
    output_file.write("from token import *\n")
    output_file.write("\n")

def visitor_imports(output_file):
    define_imports(output_file)

def define_visitor(output_dir, base_name, types):
    output_file = open(f"{output_dir}/visitor.py", mode="w+", encoding="utf-8")

    output_file.write(f"from {base_name} import *\n")
    visitor_imports(output_file)

    output_file.write(f"\nclass Visitor(ABC):\n")

    for type in types:
        type_name = type.split("|")[0].strip()
        output_file.write(f"    @abstractmethod\n")
        output_file.write(f"    def visit{type_name}{base_name}(self, {base_name.lower()}:  {type_name}):\n")
        output_file.write(f"        pass\n\n")

    output_file.close()
    print(f"[written]: {output_dir}/visitor.py")


def define_type(output_file, base_name, class_name, field_list):
    output_file.write(f"\nclass {class_name}({base_name}):\n")
    output_file.write(f"    def __init__(self, {field_list}):\n")

    # Store parameters in fields
    fields = field_list.split(", ")
    for field in fields:
        #name = field.split(" ")[1]
        name = field.strip()
        output_file.write(f"        self.{name} = {name}\n")
    output_file.write("\n")

    # Visitor Pattern
    output_file.write(f"    def accept(self, visitor):\n")
    output_file.write(f"        return visitor.visit{class_name}{base_name}(self)\n")

if __name__=="__main__":
    main()
