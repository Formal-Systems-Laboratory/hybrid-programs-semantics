Semantics of Hybrid Programs in K
==================================

We present the semantics of Hybrid Programs in K

```{.k}

module KHP-SYNTAX
    imports BOOL
    imports ID
    imports INT

    syntax ResultExp ::= Bool | Int

    syntax Exp ::= ResultExp
                 | Id
                 | Exp "+" Exp

    syntax Stmt ::= Id ":=" Exp

endmodule


module KHP
    imports KHP-SYNTAX
    imports MAP

    configuration <k> $PGM:Stmt </k>
                  <state> .Map </state>

endmodule

```
