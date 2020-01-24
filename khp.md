Semantics of Hybrid Programs in K
==================================

We describe the semantics of Hybrid Program, as presented in Differential
Dynamic Logic in K

```{.k}
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
                  | ( BExp )        [bracket]
                  | AExp ">" AExp   [strict]
                  | AExp "<" AExp   [strict]
                  | AExp ">=" AExp  [strict]
                  | AExp "<=" AExp  [strict]
                  | BExp "&&" BExp  [strict]

    syntax Exp ::= AExp
                 > BExp
```

### Discrete Assignments and Conditionals


```{.k}
    syntax Stmt ::= Id ":=" Exp     [strict(2)]
                  | Id ":=" "*"
                  | "?" BExp        [strict]
```

### Continuous Assignments (Evolutions)

```{.k}

    syntax ContAssgn ::= Id "'" "=" AExp            [strict(2)]
                       | ContAssgn "," ContAssgn    [right]

    syntax Stmt ::= ContAssgn "&" BExp

    syntax Stmts ::= Stmt
                   | "{" Stmts "}"     [bracket]
                   | "(" Stmts ")"     [bracket]
                   | Stmts "U" Stmts
                   > Stmts ";" Stmts   [right]
```

A Hybrid Program is represented as following -
 - vars `<Variables Declarations> ; <Pgm>`

where `Variable Declarations` are program variables
in the Hybrid Program.

```{.k}
    syntax VarDecl ::= Id
                     | Id "&" BExp

    syntax VarDecls ::= List{VarDecl, ","}
    syntax Pgm ::= "vars" VarDecls ";"  Stmts

endmodule
```

Main Semantics Module
---------------------

Main symbolic execution semantics

```{.k}
module KHP
    imports KHP-SYNTAX
    imports MAP


    configuration <k> $PGM:Pgm </k>
                  <state> .Map </state>

    syntax KResult ::= Bool | Int
```

Hybrid Program states are maps from program variables to Reals.
For each variable, the state is bound to a logical Variable of sort `Real`.

```{.k}
    rule <k> vars ( X:Id , L:VarDecls => L) ; _ </k>
         <state> ... .Map => (X |-> ?INITIAL:Int) ... </state>

    rule <k> vars .VarDecls ; S:Stmts => S </k>

    rule E1:Stmt ; E2:Stmts => E1 ~> E2
```

### Discrete Assignment and Lookup

```{.k}
    rule <k> (X:Id := A:Int => .) ... </k>
         <state> ... X |-> (_ => A) ... </state>
    rule <k> (X:Id := * => .) ... </k>
         <state> ... X |-> (_ => ?NONDET:Int) ... </state>

    rule <k> X:Id => V ... </k>
         <state> ... (X |-> V) ... </state>
```

### Arithmetic + Bool Expressions

 - Todo: Implement basic support for Reals

```{.k}
    rule A:Int * B:Int => A *Int B
    rule A:Int + B:Int => A +Int B

    rule A:Int > B:Int => A >Int B
    rule A:Int < B:Int => A <Int B

    rule A:Int >= B:Int => A >=Int B
    rule A:Int <= B:Int => A <=Int B

    rule A:Bool && B:Bool => A andBool B

    rule <k> ?(B:Bool) => . ... </k>
        requires B ==Bool true
```

### Nondeterminstic Choice

The choice operator `a U b`
Nondeterminstically chooses one of the sub hybrid programs.

```{.k}
    rule P1:Stmts U P2:Stmts => P1
    rule P1:Stmts U P2:Stmts => P2
```

### Continuous Evolutions

```{.k}
    rule A1:ContAssgn , A2:ContAssgn & B:BExp
      => {A1}:>ContAssgn & B ~> {A2}:>ContAssgn & B

    // Strictness not causing term to heat for some reason
    context X:Id ' = HOLE:AExp & _

endmodule
```






