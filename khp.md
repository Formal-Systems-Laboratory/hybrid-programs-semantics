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
    syntax ContBExp ::= BExp
                      | ContBExp "," ContBExp       [right]

    syntax Stmt ::= ContAssgn "&" ContBExp

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
                  <evolutionConditions> .Set </evolutionConditions>

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

The differential dynamic logic continuous evolution rule is defined as -

   ( x' = f & B ) evolves as
 - exists a T such that
    1. S(T) satisfies B
    2. S(0) = X_Initial
    3. V 0 <= t <= T . S(t) satisfies B
    4. V 0 < t < T . S'(t) = f

```{.k}

    syntax Id ::= "#appendStrToPgmVar" "(" Id "," String ")"        [function]

    rule #appendStrToPgmVar(I:Id, S:String) => String2Id(Id2String(I) +String "_traj")

    syntax ContBExp ::= "#renamePgmVars" "(" ContBExp ")"        [function]

    rule #renamePgmVars(X:Id <= A:AExp) => (#appendStrToPgmVar(X, "_traj") <= A)
    rule #renamePgmVars(X:Id >= A:AExp) => (#appendStrToPgmVar(X, "_traj") >= A)

    rule #renamePgmVars(X:Id < A:AExp) => (#appendStrToPgmVar(X, "_traj") < A)
    rule #renamePgmVars(X:Id > A:AExp) => (#appendStrToPgmVar(X, "_traj") > A)

    rule #renamePgmVars(B1:BExp, B2:ContBExp) => #renamePgmVars(B1) ,  #renamePgmVars(B2)

    rule A1:ContAssgn , A2:ContAssgn & B:ContBExp => A1 ~> A2 ~> #renamePgmVars(B)
```

### Linear Solutions

```{.k}

    syntax Trajectory ::= "#interval" "{" BExp "}" AExp

    syntax Int ::= Trajectory

    syntax KResult ::= Trajectory


    syntax KItem ::= "#intervalBoundary" "(" Int ")"

    rule <k> X:Id ' = I:Int => #intervalBoundary(?T:Int) ... </k>
         <state> ...
                (X |-> ( V => (V +Int (I *Int ?T:Int))))
                (.Map =>  #appendStrToPgmVar(X, "_traj")
                          |-> ( #interval { (0 <= ?T2:Int) && (?T2:Int <= ?T:Int) }
                                (V +Int (I *Int ?T2:Int))
                              )
                )
                ...
         </state>

    rule <k> #intervalBoundary(T) ~> X:Id ' = I:Int => #intervalBoundary(T) ... </k>
         <state> ...
                (X |-> ( V => (V +Int (I *Int T:Int))))
                (.Map =>  #appendStrToPgmVar(X, "_traj")
                          |-> ( #interval { (0 <= ?T2:Int) && (?T2:Int <= T:Int) }
                                (V +Int (I *Int ?T2:Int))
                              )
                )
                ...
         </state>
```

Mechanism to handle storing evolution conditions

```{.k}
    syntax KItem ::= "#store"
                   | "#storeDone"

    rule #intervalBoundary(_) ~> B:ContBExp => B ~> #storeDone

    rule B1:BExp , B2:ContBExp => B1 ~> #store ~> B2
    rule B1:Exp ~> #storeDone => B1 ~> #store

    rule <k> B:Bool ~> #store => . ... </k>
         <evolutionConditions> ... (.Set => SetItem(B)) ... </evolutionConditions>


endmodule
```

