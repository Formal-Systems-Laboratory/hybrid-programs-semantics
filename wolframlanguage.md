The Syntax Of Wolfram Language Expressions
==========================================

```{.k}
requires "khp-real.k"
requires "domains.k"

module WOLFRAMLANGUAGE-SYNTAX
    imports REAL-SYNTAX
    imports ID-SYNTAX

    syntax FullFormExpressionConst ::= "True"           [token]
                                     | "Reals"          [token]

    syntax FullFormExpression ::= Id
                                | FullFormExpressionConst
                                | String
                                | Real
                                | Operator "[" FullFormExpressions "]"

    syntax FullFormExpressions ::= List{FullFormExpression, ","}

    syntax Operator ::= "Plus"           [token]
                      | "Minus"          [token]
                      | "Subtract"       [token]
                      | "Times"          [token]
                      | "Divide"         [token]
                      | "Exponent"       [token]
                      | "Greater"        [token]
                      | "GreaterEqual"   [token]
                      | "Less"           [token]
                      | "LessEqual"      [token]
                      | "Equal"          [token]
                      | "And"            [token]
                      | "Implies"        [token]
                      | "ForAll"         [token]
                      | "Resolve"        [token]
                      | "Echo"           [token]
                      | "FullForm"       [token]
		      | "Exists"         [token]
                      | "Needs"          [token]
                      | "CStruct"        [token]
                      | "CTypedef"       [token]
                      | "CPointerType"   [token]
                      | "CPointerMember" [token]
                      | "CReturn"        [token]
                      | "List"           [token]
                      | "CFunction"      [token]
                      | "CExpression"    [token]
                      | "CAssign"        [token]
                      | "CBlock"         [token]
                      | "CForm"          [token]
                      | "Join"           [token]

endmodule

module WOLFRAMLANGUAGE
    imports WOLFRAMLANGUAGE-SYNTAX
    imports ID
    imports STRING

    syntax String ::= "Operator2String" "(" Operator ")"                            [function, hook(STRING.token2string)]
                    | "Const2String" "(" FullFormExpressionConst ")"                [function, hook(STRING.token2string)]
                    | "#wolfram.expressionToString"    "(" FullFormExpression ")"   [function]
                    | "#wolfram.expressionToStringAux" "(" FullFormExpressions ")"  [function]

    rule #wolfram.expressionToString(ID:Id) => Id2String(ID)
    rule #wolfram.expressionToString(REAL:RealVal) => Real2String(REAL)
    rule #wolfram.expressionToString(C:FullFormExpressionConst) => Const2String(C)
    rule #wolfram.expressionToString(S:String) => "\"" +String S +String "\""

    rule #wolfram.expressionToStringAux( E1:FullFormExpression
                                       , E2:FullFormExpression
                                       , Es:FullFormExpressions )
      => #wolfram.expressionToString(E1) +String ", " +String #wolfram.expressionToStringAux(E2,Es)

    rule #wolfram.expressionToStringAux(E1:FullFormExpression, .FullFormExpressions)
      => #wolfram.expressionToString(E1)

    rule #wolfram.expressionToString(OP:Operator [ EXPRS:FullFormExpressions ])
      => Operator2String(OP)
         +String "[" +String #wolfram.expressionToStringAux(EXPRS) +String "]"
```

A Simple Visitor for WolframLanguage ASTs
-----------------------------------------

```{.k}
    syntax Transformation

    syntax FullFormExpression ::= "#apply" "(" Transformation "|" FullFormExpression ")"                     [function]
                                | "#wolfram.map" "(" Transformation "|" FullFormExpression ")"  [function]

    syntax FullFormExpressions ::= "#wolfram.mapAux" "(" Transformation "|" FullFormExpressions ")"  [function]

    rule #wolfram.map(T | OP[ARGS] ) => OP[ #wolfram.mapAux(T | ARGS) ]

    rule #wolfram.map(T | EXP) => #apply(T | EXP) [owise]

    rule #wolfram.mapAux(T | ARG1:FullFormExpression
                           , ARG2:FullFormExpression
                           , ARGS:FullFormExpressions)
      => #wolfram.map(T | ARG1) , #wolfram.mapAux(T | ARG2, ARGS)

    rule #wolfram.mapAux(T | ARG:FullFormExpression, .FullFormExpressions)
      => #wolfram.map(T | ARG)

endmodule
```
