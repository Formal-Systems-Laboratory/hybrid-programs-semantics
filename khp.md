Semantics of Hybrid Programs in K
==================================

We describe the semantics of Hybrid Program, as presented in Differential
Dynamic Logic in K

```{.k}
requires "khp-real.k"
requires "wolframlanguage.k"

module KHP-SYNTAX
    imports BOOL
    imports ID
    imports REAL

    syntax AExp ::= Id | Real
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
                  | AExp "==" AExp  [strict]
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
    imports WOLFRAMLANGUAGE

    syntax Mode ::= "#regular"
                  | "#constraintSynthesis"

    syntax KItem ::= "#processMode" "(" Mode ")"
                   | "#synthesizeConstraints"

    syntax Ids ::= ".Ids"
                 | Id
                 | Ids "," Ids  [right]

    configuration <k> #processMode($MODE) ~> $PGM:Pgm </k>
                  <pgmVars> .Ids </pgmVars>
                  <state> .Map </state>
                  <evolutionConditions> .Set </evolutionConditions>

    rule #processMode(#regular) ~> P:Pgm => P
    rule #processMode(#constraintSynthesis) ~> P:Pgm => P ~> #synthesizeConstraints

    syntax KResult ::= Bool | Real
```

Hybrid Program states are maps from program variables to Reals.
For each variable, the state is bound to a logical Variable of sort `Real`.

```{.k}
    rule <k> vars ( X:Id , L:VarDecls => L) ; _ ... </k>
         <state> ... .Map => (X |-> ?INITIAL:Real) ... </state>
         <pgmVars> PGM_IDS => X, PGM_IDS </pgmVars>
         <evolutionConditions>
            ...
            (.Set => SetItem(#appendStrToPgmVar(X, "_i") == ?INITIAL:Real))
            ...
         </evolutionConditions>

    rule vars .VarDecls ; S:Stmts => S
    syntax FullFormExpression ::= "#toWolframExpression" "(" BExp ")" [function]

    rule E1:Stmt ; E2:Stmts => E1 ~> E2
```

### Discrete Assignment and Lookup

```{.k}
    rule <k> (X:Id := A:Real => .) ... </k>
         <state> ... X |-> (_ => A) ... </state>
    rule <k> (X:Id := * => .) ... </k>
         <state> ... X |-> (_ => ?NONDET:Real) ... </state>

    rule <k> X:Id => V ... </k>
         <state> ... (X |-> V) ... </state>
```

### Arithmetic + Bool Expressions

 - Todo: Implement basic support for Reals

```{.k}
    rule A:Real * B:Real => A *Real B
    rule A:Real + B:Real => A +Real B

    rule A:Real > B:Real => A >Real B
    rule A:Real < B:Real => A <Real B

    rule A:Real >= B:Real => A >=Real B
    rule A:Real <= B:Real => A <=Real B

    rule A:Bool && B:Bool => A andBool B

    rule <k> ?(B:Bool) => . ... </k>
         <evolutionConditions> ... (.Set => SetItem(B)) ... </evolutionConditions>
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

    rule #appendStrToPgmVar(I:Id, S:String) => String2Id(Id2String(I) +String S)

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

    syntax QuantifiedReal ::= "#quantified" "(" Real ")"
    syntax Trajectory ::= "#interval" "{" QuantifiedReal "," BExp "}" AExp

    syntax Real ::= Trajectory

    syntax KResult ::= Trajectory

    syntax Bool ::= Trajectory "<Trajectory" Exp
                  | Trajectory ">Trajectory" Exp
                  | Trajectory "<=Trajectory" Exp
                  | Trajectory ">=Trajectory" Exp

    rule T:Trajectory <=Real R:Real => T <=Trajectory R
    rule T:Trajectory >=Real R:Real => T >=Trajectory R
    rule T:Trajectory <Real R:Real => T <Trajectory R
    rule T:Trajectory >Real R:Real => T >Trajectory R

    syntax KItem ::= "#intervalBoundary" "(" Real ")"
    syntax FullFormExpression ::= "#toWolframExpression" "(" BExp ")" [function]

    rule <k> X:Id ' = I:Real => #intervalBoundary(?T:Real) ... </k>
         <state> ...
                (X |-> ( V => (V +Real (I *Real ?T:Real))))
                (.Map =>  #appendStrToPgmVar(X, "_traj")
                          |-> ( #interval { #quantified(?T2:Real)
                                            , ({0.0}:>Real <=Real ?T2:Real) &&
                                              (?T2:Real <=Real ?T:Real)
                                          }
                                (V +Real (I *Real ?T2:Real))
                              )
                )
                ...
         </state>

    rule <k> #intervalBoundary(T) ~> X:Id ' = I:Real => #intervalBoundary(T) ... </k>
         <state> ...
                (X |-> ( V => (V +Real (I *Real T:Real))))
                (.Map =>  #appendStrToPgmVar(X, "_traj")
                          |-> ( #interval { #quantified(?T2:Real)
                                          , ({0.0}:>Real <=Real ?T2:Real) &&
                                            (?T2:Real <=Real T:Real)
                                          }
                                (V +Real (I *Real ?T2:Real))
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
```

### Constraint Synthesis

```{.k}
    syntax FullFormExpression ::= "#toWolframExpression" "(" Exp ")" [function]

    rule #toWolframExpression(X:Id) => X
    rule #toWolframExpression(R:Real) => R

    rule #toWolframExpression(A && B) => And[ #toWolframExpression(A)
                                            , #toWolframExpression(B)]
    rule #toWolframExpression(A == B) => Equal[ #toWolframExpression(A)
                                              , #toWolframExpression(B)]

    rule #toWolframExpression(A ==Real B) => Equal[ #toWolframExpression(A)
                                                  , #toWolframExpression(B)]
    rule #toWolframExpression(A <=Real B) => LessEqual[ #toWolframExpression(A)
                                                      , #toWolframExpression(B)]
    rule #toWolframExpression(A >=Real B) => GreaterEqual[ #toWolframExpression(A)
                                                         , #toWolframExpression(B)]
    rule #toWolframExpression(A <Real B) => Less[ #toWolframExpression(A)
                                                , #toWolframExpression(B)]
    rule #toWolframExpression(A >Real B) => Greater[ #toWolframExpression(A)
                                                   , #toWolframExpression(B)]

    rule #toWolframExpression(A +Real B) => Plus[ #toWolframExpression(A)
                                                , #toWolframExpression(B)]
                                                [concrete]
    rule #toWolframExpression(A -Real B) => Minus[ #toWolframExpression(A)
                                                 , #toWolframExpression(B)]
    rule #toWolframExpression(A *Real B) => Times[ #toWolframExpression(A)
                                                 , #toWolframExpression(B)]
    rule #toWolframExpression(A /Real B) => Divide[ #toWolframExpression(A)
                                                  , #toWolframExpression(B)]

    rule #toWolframExpression( #interval { #quantified(VAR) , CONSTRAINT }
                                    EVOLUTION >=Trajectory DOMAIN )
      => ForAll[ #toWolframExpression(VAR)
               , Implies[ #toWolframExpression(CONSTRAINT)
                        , GreaterEqual[ #toWolframExpression(EVOLUTION)
                                      , #toWolframExpression(DOMAIN)
                                      ]
                        ]
               ]

    rule #toWolframExpression( #interval { #quantified(VAR) , CONSTRAINT }
                                    EVOLUTION <=Trajectory DOMAIN )
      => ForAll[ #toWolframExpression(VAR)
               , Implies[ #toWolframExpression(CONSTRAINT)
                        , LessEqual[ #toWolframExpression(EVOLUTION)
                                   , #toWolframExpression(DOMAIN)
                                   ]
                        ]
               ]

    rule #toWolframExpression( #interval { #quantified(VAR) , CONSTRAINT }
                                    EVOLUTION <Trajectory DOMAIN )
      => ForAll[ #toWolframExpression(VAR)
               , Implies[ #toWolframExpression(CONSTRAINT)
                        , Less[ #toWolframExpression(EVOLUTION)
                              , #toWolframExpression(DOMAIN)
                              ]
                        ]
               ]

    rule #toWolframExpression( #interval { #quantified(VAR) , CONSTRAINT }
                                    EVOLUTION >Trajectory DOMAIN )
      => ForAll[ #toWolframExpression(VAR)
               , Implies[ #toWolframExpression(CONSTRAINT)
                        , Greater[ #toWolframExpression(EVOLUTION)
                                 , #toWolframExpression(DOMAIN)
                                 ]
                        ]
               ]
    syntax KItem ::= "#constraints" "(" FullFormExpression ")"
                   | "#processEvolutionConstraints"
                   | "#processFinalStateConstraints"


    rule <k> #synthesizeConstraints => #processEvolutionConstraints ~> #constraints(And[True]) </k>

    rule <k> #processEvolutionConstraints
          ~> #constraints(And[E => (#toWolframExpression(B), E)]) </k>
         <evolutionConditions> ... (SetItem(B) => .Set) ...  </evolutionConditions>

    rule <k> #processEvolutionConstraints ~> CONSTRAINTS => #processFinalStateConstraints ~> CONSTRAINTS </k>
         <evolutionConditions> .Set </evolutionConditions>

    rule <k> #processFinalStateConstraints ~>
             #constraints(And[E => (#toWolframExpression((HEAD == VAL)), E)]) </k>
         <pgmVars> (HEAD:Id , REST:Ids) => REST </pgmVars>
         <state> ... (ID |-> VAL) ... </state>

    rule <k> #processFinalStateConstraints ~> CONSTRAINTS => CONSTRAINTS </k>
         <pgmVars> .Ids </pgmVars>
endmodule
```

