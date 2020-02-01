The Syntax Of Wolfram Language Expressions
==========================================

```{.k}
requires "khp-real.k"
module WOLFRAMLANGUAGE-SYNTAX
    imports REAL-SYNTAX
    imports ID
    imports STRING

    syntax FullFormExpression ::= Id
                                | Real
                                | "True"    [token]
                                | "Reals"   [token]
                                | Operator "[" FullFormExpressions "]"

    syntax FullFormExpressions ::= List{FullFormExpression, ","}

    syntax Operator ::= "Plus"         [token]
                      | "Minus"        [token]
                      | "Times"        [token]
                      | "Divide"       [token]
                      | "Exponent"     [token]
                      | "Greater"      [token]
                      | "GreaterEqual" [token]
                      | "Less"         [token]
                      | "LessEqual"    [token]
                      | "Equal"        [token]
                      | "And"          [token]
                      | "Implies"      [token]
                      | "ForAll"       [token]
                      | "Resolve"      [token]

    syntax String ::= "Operator2String" "(" Operator ")"                            [function, hook(STRING.token2string)]
                    | "#toWolframExpressionString"    "(" FullFormExpression ")"    [function]
                    | "#toWolframExpressionStringAux" "(" FullFormExpressions ")"   [function]

endmodule

module WOLFRAMLANGUAGE
    imports WOLFRAMLANGUAGE-SYNTAX

    rule #toWolframExpressionString(ID:Id) => Id2String(ID)
    rule #toWolframExpressionString(REAL:Real) => Real2String(REAL)
    rule #toWolframExpressionString(True) => "True"
    rule #toWolframExpressionString(Reals) => "Reals"

    rule #toWolframExpressionStringAux(E1:FullFormExpression , E2:FullFormExpressions)
      => #toWolframExpressionString(E1) +String ", " +String #toWolframExpressionStringAux(E2)

    rule #toWolframExpressionStringAux(E1:FullFormExpression, .FullFormExpressions)
      => #toWolframExpressionString(E1)

    rule #toWolframExpressionString(OP:Operator [ EXPRS:FullFormExpressions ])
      => Operator2String(OP)
         +String "[" +String #toWolframExpressionStringAux(EXPRS) +String "]"

endmodule

```
