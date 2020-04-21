Basic Reals Implementation
==========================

```{.k}
require "substitution.k"
module REAL-SYNTAX
    imports BOOL-SYNTAX
    imports STRING-SYNTAX
    imports STRING
    imports ID

    syntax RealVal ::= r"[\\+-]?[0-9]+\\.[0-9]*"  [token, prefer, prec(1)]

    syntax RealVar ::= "#VarReal" "(" Id ")"

    syntax Real ::= RealVal
                  | RealVar
                  | Real "/Real" Real   
                  | Real "*Real" Real   
                  | Real "^Real" Real   
                  > Real "+Real" Real   
                  | Real "-Real" Real   

    syntax String ::= "Real2String" "(" Real ")" [function, hook(STRING.token2string)]

    syntax Bool  ::= Real ">Real" Real  
                   | Real "<Real" Real  
                   | Real ">=Real" Real 
                   | Real "<=Real" Real 
                   | Real "!=Real" Real 
                   | Real "==Real" Real 

endmodule

module REAL
    imports REAL-SYNTAX
    imports SUBSTITUTION
    imports K-IO
endmodule
```
