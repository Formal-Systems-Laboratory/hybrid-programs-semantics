Basic Reals Implementation
==========================

```{.k}
require "substitution.k"
module REAL-SYNTAX
    imports ID-SYNTAX

    syntax RealVal ::= r"[\\+-]?[0-9]+\\.[0-9]*"  [token, prefer, prec(2)]

    syntax RealVar ::= "#VarReal" "(" Id ")"

    syntax Real ::= RealVal
                  | RealVar

    syntax String ::= "Real2String" "(" RealVal ")" [function, hook(STRING.token2string)]

endmodule

module REAL
    imports REAL-SYNTAX
endmodule
```
