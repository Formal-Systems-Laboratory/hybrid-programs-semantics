Semantics of Hybrid Programs in K
==================================

We describe the semantics of Hybrid Program, as presented in Differential
Dynamic Logic in K

```{.k}
module KHP-SYNTAX
    imports BOOL
    imports ID
    imports INT

    syntax AExp ::= Id | Int
                 | ( AExp )        [bracket]
                 | AExp "*" AExp   [strict, left]
                 | AExp "/" AExp   [strict, left]
                 > AExp "+" AExp   [strict, left]
                 | AExp "-" AExp   [strict, left]

    syntax BExp ::= Bool
                  | ( BExp )        [bracket]
                  | AExp ">" AExp   [strict]
                  | AExp "<" AExp   [strict]
                  | AExp ">=" AExp  [strict]
                  | AExp "<=" AExp  [strict]

    syntax Exp ::= AExp
                 > BExp

    syntax Stmt ::= Id ":=" Exp     [strict(2)]
                  | "?" BExp        [strict]

    syntax Stmts ::= Stmt
                   | Stmts ";" Stmts   [right]
```

A Hybrid Program is represented as following -
 - vars `<Variables Declarations> ; <Pgm>`

where `Variable Declarations` are program variables
in the Hybrid Program.

```{.k}
    syntax VarDecl ::= Id
                     | Id "&" BExp

    syntax VarDecls ::= List{VarDecl, ","}
    syntax Pgm ::= "vars" VarDecls ";"  Stmts

endmodule
```

Main Semantics Module
---------------------

Main symbolic execution semantics

```{.k}
module KHP
    imports KHP-SYNTAX
    imports MAP


    configuration <k> $PGM:Pgm </k>
                  <state> .Map </state>

    syntax KResult ::= Bool | Int
```

Hybrid Program states are maps from program variables to Reals.
For each variable, the state is bound to a logical Variable of sort `Real`.

```{.k}
    rule <k> vars ( X:Id , L:VarDecls => L) ; _ </k>
         <state> ... .Map => (X |-> ?I:Int) ... </state>

    rule <k> vars .VarDecls ; S:Stmts => S </k>

    rule E1:Stmt ; E2:Stmts => E1 ~> E2
```

### Discrete Assignment and Lookup

```{.k}
    rule <k> (X:Id := A:Int => .) ... </k>
         <state> ... X |-> (_ => A) ... </state>

    rule <k> X:Id => V ... </k>
         <state> ... (X |-> V) ... </state>
```

### Arithmetic + Bool Expressions

 - Todo: Switch or implement support for Reals

```{.k}
    rule A:Int * B:Int => A *Int B
    rule A:Int + B:Int => A +Int B

    rule A:Int > B:Int => A >Int B
    rule A:Int < B:Int => A <Int B
    rule A:Int >= B:Int => A >=Int B
    rule A:Int <= B:Int => A <=Int B

    rule <k> ?(B:Bool) => . ... </k>
        requires B ==Bool true

    syntax KItem ::= "#abort"
    rule <k> ?(B:Bool) ~> _ => #abort </k>
        requires B ==Bool false

endmodule
```
