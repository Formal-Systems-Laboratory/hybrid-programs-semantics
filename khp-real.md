Basic Reals Implementation
==========================

```{.k}
require "substitution.k"
module REAL-SYNTAX
    imports BOOL-SYNTAX
    imports STRING-SYNTAX
    imports STRING
    imports ID

    syntax RealVal ::= r"[0-9]+\\.[0-9]*"  [token, prefer, prec(1)]

    syntax RealVar ::= "#VarReal" "(" Id ")"

    syntax Real ::= RealVal
                  | RealVar
                  | Real "/Real" Real   [function]
                  | Real "*Real" Real   [function]
                  | Real "^Real" Real   [function]
                  > Real "+Real" Real   [function]
                  | Real "-Real" Real   [function]

    syntax String ::= "Real2String" "(" Real ")" [function, hook(STRING.token2string)]

    syntax Bool  ::= Real ">Real" Real   [function]
                   | Real "<Real" Real   [function]
                   | Real ">=Real" Real  [function]
                   | Real "<=Real" Real  [function]
                   | Real "!=Real" Real  [function]
                   | Real "==Real" Real  [function]

endmodule

module REAL
    imports REAL-SYNTAX
    imports SUBSTITUTION
    imports K-IO

    syntax KItem ::= "#processResult" "(" KItem ")" [function]

    rule #processResult(#systemResult(0, S, _))
      => #parseToken( "Real"
                    , substrString(S, 0, lengthString(S) -Int 1)
                    )


    rule #processResult(#systemResult(0, "True\n", _)) => {true}:>Bool
    rule #processResult(#systemResult(0, "False\n", _)) => {false}:>Bool

    rule A:RealVal +Real B:RealVal => { #processResult( #system( "wolframscript -c "
                                                               +String Real2String(A)
                                                               +String "+"
                                                               +String Real2String(B)
                                                               )
                                                      )
                                      }:>Real    [anywhere]

    rule A:RealVal -Real B:RealVal => { #processResult( #system( "wolframscript -c "
                                                              +String Real2String(A)
                                                              +String "-"
                                                              +String Real2String(B)
                                                              )
                                                     )
                                     }:>Real    [anywhere]

    rule A:RealVal *Real B:RealVal => { #processResult( #system( "wolframscript -c "
                                                               +String Real2String(A)
                                                               +String "*"
                                                               +String Real2String(B)
                                                               )
                                                      )
                                      }:>Real    [anywhere]

    rule A:RealVal /Real B:RealVal => { #processResult( #system( "wolframscript -c "
                                                               +String Real2String(A)
                                                               +String "/"
                                                               +String Real2String(B)
                                                               )
                                                      )
                                      }:>Real    [anywhere]

    rule A:RealVal ^Real B:RealVal => { #processResult( #system( "wolframscript -c "
                                                               +String Real2String(A)
                                                               +String "^"
                                                               +String Real2String(B)
                                                               )
                                                      )
                                      }:>Real    [anywhere]

    rule A:RealVal ==Real B:RealVal => { #processResult( #system( "wolframscript -c "
                                                                +String Real2String(A)
                                                                +String "=="
                                                                +String Real2String(B)
                                                                )
                                                       )
                                       }:>Bool

    rule A:RealVal >=Real B:RealVal => { #processResult( #system( "wolframscript -c "
                                                                +String Real2String(A)
                                                                +String ">="
                                                                +String Real2String(B)
                                                                )
                                                       )
                                       }:>Bool

    rule A:RealVal <=Real B:RealVal => { #processResult( #system( "wolframscript -c "
                                                                +String Real2String(A)
                                                                +String "<="
                                                                +String Real2String(B)
                                                                )
                                                       )
                                       }:>Bool

    rule A:RealVal <Real B:RealVal => { #processResult( #system( "wolframscript -c "
                                                               +String Real2String(A)
                                                               +String "<"
                                                               +String Real2String(B)
                                                               )
                                                      )
                                       }:>Bool

    rule A:RealVal >Real B:RealVal => { #processResult( #system( "wolframscript -c "
                                                               +String Real2String(A)
                                                               +String ">"
                                                               +String Real2String(B)
                                                               )
                                                      )
                                       }:>Bool
endmodule
```
