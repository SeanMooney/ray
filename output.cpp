start
  variable_define
    type_name	I32
    name	my_int
    :=
    literal_value
      number	10
    ;
  commnet	# this is a comment
  variable_define
    type_name	I32
    name	my_hex_int
    :=
    literal_value
      number	0xff
    ;
  variable_define
    type_name	I32
    name	my_octal_int
    :=
    literal_value
      number	0o1
    ;
  variable_define
    type_name	I32
    name	my_bin_int
    :=
    literal_value
      number	0b11
    ;
  variable_define
    type_name	F32
    name	my_float
    :=
    literal_value
      number	0.0
    ;
  function_define
    type_name	Void
    name	freeFunction
    (
    )
    {
    commnet	# print("this is a test");
    variable_define
      type_name	I32
      name	i
      :=
      literal_value
        number	1
      ;
    }
  block_statement
    {
    }
  class_define
    type_name	MyStruct
    :
    type_name	Parent
    {
    variable_declaration
      type_name	Bool
      name	my_class_var
      ;
    function_define
      type_name	Void
      name	memberFunction
      (
      )
      {
      commnet	# print("this is a test");
      variable_define
        type_name	I32
        name	i
        :=
        literal_value
          number	1
        ;
      assignment_statement
        name	i
        :=
        runtime_value
          bin_expression
            literal_value
              number	1
            expression_operator	+
            literal_value
              number	1
        ;
      assignment_statement
        name	i
        :=
        runtime_value
          uniary_expression
            expression_operator	-
            runtime_value
              name	i
        ;
      commnet	#i += 1;
      expression_satement
        call_expression
          name	myOtherFunc
          (
          )
        ;
      expression_satement
        bin_expression
          literal_value
            number	1
          expression_operator	+
          literal_value
            number	2
        ;
      }
    function_define
      type_name	Void
      name	myOtherFunc
      (
      )
      {
      }
    }
  commnet	# define int main(I32: argc, string[] args){
  commnet	#     print("hello world");
  commnet	#     retrun 0;
  commnet	# }

