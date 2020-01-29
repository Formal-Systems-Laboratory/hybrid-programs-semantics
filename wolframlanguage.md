The Syntax Of Wolfram Language Expressions
==========================================

```{.k}
requires "khp-reals.k"
module WOLFRAMLANGUAGE-SYNTAX
    imports REAL-SYNTAX
    imports ID

    syntax FullFormExpressions ::= Operator Operands

    syntax Operator ::= "Plus"
    syntax Operands ::= Id
                      | Real
endmodule

```
