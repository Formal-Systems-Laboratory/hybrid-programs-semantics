Basic Reals Implementation
==========================

```{.k}
require "substitution.k"
module REAL-SYNTAX
    imports BOOL-SYNTAX
    imports STRING-SYNTAX
    imports STRING

    syntax Real ::= r"[0-9]+\\.[0-9]*"  [token, prefer, prec(2)]
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

    rule A +Real B => { #processResult( #system( "wolframscript -c "
                                               +String Real2String(A)
                                               +String "+"
                                               +String Real2String(B)
                                               )
                                      )
                      }:>Real	[concrete]

    rule A -Real B => { #processResult( #system( "wolframscript -c "
                                               +String Real2String(A)
                                               +String "-"
                                               +String Real2String(B)
                                               )
                                      )
                      }:>Real	[concrete]

    rule A *Real B => { #processResult( #system( "wolframscript -c "
                                               +String Real2String(A)
                                               +String "*"
                                               +String Real2String(B)
                                               )
                                      )
                      }:>Real	[concrete]

    rule A /Real B => { #processResult( #system( "wolframscript -c "
                                               +String Real2String(A)
                                               +String "/"
                                               +String Real2String(B)
                                               )
                                      )
                      }:>Real	[concrete]

    rule A ^Real B => { #processResult( #system( "wolframscript -c "
                                               +String Real2String(A)
                                               +String "^"
                                               +String Real2String(B)
                                               )
                                      )
                      }:>Real	[concrete]

    rule A ==Real B => { #processResult( #system( "wolframscript -c "
                                                +String Real2String(A)
                                                +String "=="
                                                +String Real2String(B)
                                                )
                                       )
                       }:>Bool	[concrete]

    rule A >=Real B => { #processResult( #system( "wolframscript -c "
                                                +String Real2String(A)
                                                +String ">="
                                                +String Real2String(B)
                                                )
                                       )
                       }:>Bool	[concrete]

    rule A <=Real B => { #processResult( #system( "wolframscript -c "
                                                +String Real2String(A)
                                                +String "<="
                                                +String Real2String(B)
                                                )
                                       )
                       }:>Bool	[concrete]

    rule A <Real B => { #processResult( #system( "wolframscript -c "
                                               +String Real2String(A)
                                               +String "<"
                                               +String Real2String(B)
                                               )
                                      )
                       }:>Bool	[concrete]

    rule A >Real B => { #processResult( #system( "wolframscript -c "
                                               +String Real2String(A)
                                               +String ">"
                                               +String Real2String(B)
                                               )
                                      )
                       }:>Bool	[concrete]
endmodule
```