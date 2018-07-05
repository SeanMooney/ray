start
  variable_define
    scalar_type_name	I32
    name	my_int
    :=
    literal_value
      number	10
    ;
  commnet	# this is a comment
  variable_define
    scalar_type_name	I32
    name	my_hex_int
    :=
    literal_value
      number	0xff
    ;
  variable_define
    scalar_type_name	I32
    name	my_octal_int
    :=
    literal_value
      number	0o1
    ;
  variable_define
    scalar_type_name	I32
    name	my_bin_int
    :=
    literal_value
      number	0b11
    ;
  variable_define
    scalar_type_name	F32
    name	my_float
    :=
    literal_value
      number	0.0
    ;
  variable_define
    scalar_type_name	String
    name	my_string
    :=
    literal_value
      string	"this is a string"
      string	' as is this'
      string	"""
                    and this
                    """
      string	''' they will all 
                    be appended'''
    ;
  function_define
    scalar_type_name	Void
    name	freeFunction
    (
    )
    {
    expression_satement
      call_expression
        name	print
        (
        arguments
          literal_value
            string	"this is a test"
        )
      ;
    variable_define
      scalar_type_name	I32
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
    scalar_type_name	MyStruct
    :
    scalar_type_name	Parent
    {
    variable_declaration
      scalar_type_name	Bool
      name	my_class_var
      ;
    function_define
      scalar_type_name	Void
      name	memberFunction
      (
      )
      {
      expression_satement
        call_expression
          name	print
          (
          arguments
            name	message
            :=
            literal_value
              string	"this is a test"
          )
        ;
      variable_define
        scalar_type_name	I32
        name	i
        :=
        literal_value
          number	1
        ;
      assignment_statement
        name	i
        :=
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
        uniary_expression
          expression_operator	-
          runtime_value
            name	i
        ;
      assignment_statement
        name	i
        +=
        literal_value
          number	1
        ;
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
      scalar_type_name	Void
      name	myOtherFunc
      (
      )
      {
      }
    }
  function_define
    scalar_type_name	Void
    name	print
    (
    paramaters
      scalar_type_name	String
      :
      name	message
    )
    {
    }
  function_define
    scalar_type_name	I32
    name	main
    (
    paramaters
      scalar_type_name	I32
      :
      name	argc
      ,
      aggregate_type_name
        String
        [
        ]
      :
      name	args
    )
    {
    expression_satement
      call_expression
        name	print
        (
        arguments
          literal_value
            string	"hello world"
        )
      ;
    return_statement
      literal_value
        number	0
      ;
    }

