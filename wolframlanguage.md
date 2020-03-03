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
                      | "Subtract"     [token]
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
                      | "Echo"         [token]
                      | "FullForm"     [token]

    syntax String ::= "Operator2String" "(" Operator ")"                            [function, hook(STRING.token2string)]
                    | "#wolfram.expressionToString"    "(" FullFormExpression ")"   [function]
                    | "#wolfram.expressionToStringAux" "(" FullFormExpressions ")"  [function]

endmodule

module WOLFRAMLANGUAGE
    imports WOLFRAMLANGUAGE-SYNTAX

    rule #wolfram.expressionToString(ID:Id) => Id2String(ID)
    rule #wolfram.expressionToString(REAL:Real) => Real2String(REAL)
    rule #wolfram.expressionToString(True) => "True"
    rule #wolfram.expressionToString(Reals) => "Reals"

    rule #wolfram.expressionToStringAux(E1:FullFormExpression , E2:FullFormExpressions)
      => #wolfram.expressionToString(E1) +String ", " +String #wolfram.expressionToStringAux(E2)

    rule #wolfram.expressionToStringAux(E1:FullFormExpression, .FullFormExpressions)
      => #wolfram.expressionToString(E1)

    rule #wolfram.expressionToString(OP:Operator [ EXPRS:FullFormExpressions ])
      => Operator2String(OP)
         +String "[" +String #wolfram.expressionToStringAux(EXPRS) +String "]"

endmodule

```
