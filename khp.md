Semantics of Hybrid Programs in K
==================================

We present the semantics of Hybrid Programs in K

```{.k}

module KHP-MAP

endmodule

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

    syntax VarDecl ::= Id
                     | Id "&" BExp

    syntax VarDecls ::= List{VarDecl, ","}
    syntax Pgm ::= "vars" VarDecls ";"  Stmts

endmodule


module KHP
    imports KHP-SYNTAX
    imports MAP


    configuration <k> $PGM:Pgm </k>
                  <state> .Map </state>

    syntax KResult ::= Bool | Int

    rule <k> vars ( X:Id , L:VarDecls => L) ; _ </k>
         <state> ... .Map => (X |-> ?I:Int) ... </state>

    rule <k> vars .VarDecls ; S:Stmts => S </k>

    rule E1:Stmt ; E2:Stmts => E1 ~> E2

    rule <k> (X:Id := A:Int => .) ... </k>
         <state> ... X |-> (_ => A) ... </state>

    rule A:Int * B:Int => A *Int B
    rule A:Int + B:Int => A +Int B

    rule <k> X:Id => V ... </k>
         <state> ... (X |-> V) ... </state>


endmodule

```
