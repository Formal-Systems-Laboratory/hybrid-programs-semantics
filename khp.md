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
    imports INT
    imports REAL


    syntax AExp ::= Id | Real
                 | ( AExp )        [bracket]
                 | AExp "*" AExp   [strict, left]
                 | AExp "/" AExp   [strict, left]
                 > AExp "+" AExp   [strict, left]
                 | AExp "-" AExp   [strict, left]

    syntax BExp ::= Bool
                  | AExp ">" AExp   [strict]
                  | AExp "<" AExp   [strict]
                  | AExp ">=" AExp  [strict]
                  | AExp "==" AExp  [strict]
                  | AExp "<=" AExp  [strict]
                  > BExp "&&" BExp  [strict]
                  > ( BExp )        [bracket]

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
 - params `[Pameter Declarations] ; vars <Variables Declarations> ; <Pgm>`

where `Variable Declarations` are program variables
in the Hybrid Program.

```{.k}
    syntax VarDecl ::= Id
                     | Id "&" BExp


    //Todo: Params are not necessarily variables

    syntax Decls ::= List{VarDecl, ","}

    syntax VarDecls ::= "vars" Decls
    syntax ParamDecls ::= "params" Decls

    syntax Pgm ::= VarDecls ";"  Stmts
                 | ParamDecls ";" VarDecls ";" Stmts

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
    imports K-IO

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
                  <nonDetAssignments> .Map </nonDetAssignments>
                  <counter> 0 </counter>

    rule #processMode(#regular) ~> P:Pgm => P
    rule #processMode(#constraintSynthesis) ~> P:Pgm => P ~> #synthesizeConstraints

    syntax KResult ::= Bool | Real

    syntax RealVar ::= #freshVar(Id, Int)   [function]

    rule #freshVar(ID, INT) => #VarReal(String2Id( Id2String(ID)
                                                 +String Int2String(INT)))

```

Hybrid Program states are maps from program variables to Reals.
For each variable, the state is bound to a logical Variable of sort `Real`.

```{.k}
    rule <k> params ( X:Id , L:Decls => L) ; _ ; _ ... </k>
         <state> ... .Map => (X |-> #VarReal(X)) ... </state>

         rule params .Decls ; VARDECLS ; S:Stmts => VARDECLS ; S

    rule <k> vars ( X:Id , L:Decls => L) ; _ ... </k>
         <state> ... .Map => (X |-> #VarReal(X)) ... </state>
         <pgmVars> PGM_IDS => X, PGM_IDS </pgmVars>

    rule vars .Decls ; S:Stmts => S

    rule E1:Stmt ; E2:Stmts => E1 ~> E2
```

### Discrete Assignment and Lookup

```{.k}
    rule <k> (X:Id := A:Real => .) ... </k>
         <state> ... X |-> (_ => A) ... </state>
    rule <k> (X:Id := * => .) ... </k>
         <state> ... X |-> (_ => #freshVar(X, I)) ... </state>
         <counter> I:Int => I +Int 1 </counter>
         <nonDetAssignments> ... (.Map => (X |-> #freshVar(X, I))) ...  </nonDetAssignments>

    rule <k> X:Id => V ... </k>
         <state> ... (X |-> V) ... </state>
```

### Arithmetic + Bool Expressions

 - Todo: Implement basic support for Reals

```{.k}
    rule A:Real * B:Real => A *Real B
    rule A:Real + B:Real => A +Real B
    rule A:Real - B:Real => A -Real B
    rule A:Real / B:Real => A /Real B

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
    4. V 0 < t < T . S'(t) = f and T' = 1

```{.k}
    syntax Id ::= "#appendStrToPgmVar" "(" Id "," String ")"        [function]
                | "#prependStrToPgmVar" "(" String "," Id ")"       [function]

    rule #appendStrToPgmVar(I:Id, S:String) => String2Id(Id2String(I) +String S)
    rule #prependStrToPgmVar(S:String, I:Id) => String2Id(S +String Id2String(I))

    syntax ContBExp ::= "#renamePgmVars" "(" ContBExp ")"        [function]

    rule #renamePgmVars(X:Id <= A:AExp) => (#appendStrToPgmVar(X, "_traj") <= A)
    rule #renamePgmVars(X:Id >= A:AExp) => (#appendStrToPgmVar(X, "_traj") >= A)

    rule #renamePgmVars(X:Id < A:AExp) => (#appendStrToPgmVar(X, "_traj") < A)
    rule #renamePgmVars(X:Id > A:AExp) => (#appendStrToPgmVar(X, "_traj") > A)

    rule #renamePgmVars(B1:BExp, B2:ContBExp) => #renamePgmVars(B1) ,  #renamePgmVars(B2)

    rule A1:ContAssgn , A2:ContAssgn & B:ContBExp => A1 ~> A2 ~> #renamePgmVars(B)
```

### Linear Solutions

An inequality over a trajectory holds
when all points in the trajectory respect it.

```{.k}

    syntax QuantifiedReal ::= "#quantified" "(" Real ")"
    syntax Trajectory ::= "#interval" "{" QuantifiedReal "," BExp "}" AExp


    syntax AExp ::= Trajectory
    syntax KResult ::= Trajectory

    syntax Bool ::= Trajectory "<Trajectory" Exp
                  | Trajectory ">Trajectory" Exp
                  | Trajectory "<=Trajectory" Exp
                  | Trajectory ">=Trajectory" Exp

    rule T:Trajectory <= R:Real => T <=Trajectory R
    rule T:Trajectory >= R:Real => T >=Trajectory R
    rule T:Trajectory < R:Real => T <Trajectory R
    rule T:Trajectory > R:Real => T >Trajectory R

    syntax KItem ::= "#intervalBoundary" "(" Real ")"
                   | "#evolutionVariable" "(" Real ")"

```

In order to give the semantics to a continuous evolution
of the form `X ' = I`, where I is a constrant or a symbolic
real-valued variable, we need to take the following steps -

 1) `X ' = I` desribes how one particular program state-variable
     evolves w.r.t. time. Time however is shared across
     evolutions of all program variables of the continuous evolution
     statement. For instance, if we have `x' = a, y' = b & BOUNDARY`,
     then there exists some `T >= 0` such that `x := sol_x(T), y := sol_y(T)`
     where `sol_x` and `sol_y` are the solutions of the differential
     equations for `x, y` respectively.

 2) Thus, in order to give semantics to `X' = I`, we first need
    an `boundary (T)` and an `evolution variable (t)`, which
    gives to `X := \exists (T >= 0) . sol_x(T)` and
    `X_traj := #interval{ }(DE-Solution)`.
    which can be interpreted as the trajectory of `X` is bound to
    a solution of the differential equation.

Note the bound for continuous evolution is instantiated with
a real valued variable `t_post`. This operation corresponds
to the skolemization proof rule in differential dynamic logic.

```{.k}

    rule <k> X:Id ' = I:Real
      =>   #evolutionVariable(#freshVar(String2Id("tpost") , COUNTER))
        ~> #intervalBoundary(#VarReal(String2Id("tpost"))) ~> X ' = I
           ...
         </k>
         <counter> COUNTER => COUNTER +Int 1 </counter>
         <evolutionConditions> ...
            (.Set => SetItem(#VarReal(String2Id("tpost")) >=Real 0.0)) ...  </evolutionConditions>

    rule <k>   #evolutionVariable(E_VAR)
            ~> #intervalBoundary(BOUND) ~> X ' = I
      =>   #intervalBoundary(BOUND)
           ...
         </k>
         <state> ...
                X |-> ( V => (V +Real (I *Real BOUND)) )
                (.Map =>  (#appendStrToPgmVar(X, "_traj")
                            |-> ( #interval { #quantified(E_VAR)
                                            , ({0.0}:>Real <=Real E_VAR) &&
                                              (E_VAR <=Real BOUND)
                                          }
                                (V +Real (I *Real E_VAR))
                                )
                           )
                )
                ...
         </state>

    rule <k> #intervalBoundary(#VarReal(VARNAME)) ~> X ' = I
      =>       #evolutionVariable(#freshVar(VARNAME, COUNTER))
            ~> #intervalBoundary(#VarReal(VARNAME)) ~> X ' = I
           ...
         </k>
         <counter> COUNTER => COUNTER +Int 1 </counter>
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
    rule #toWolframExpression(R:RealVal) => R
    rule #toWolframExpression(#VarReal(ID)) => ID

    rule #toWolframExpression(A && B) => And[ #toWolframExpression(A)
                                            , #toWolframExpression(B)]
    rule #toWolframExpression(A == B) => Equal[ #toWolframExpression(A)
                                              , #toWolframExpression(B)]

    rule #toWolframExpression(A andBool B) => And[ #toWolframExpression(A)
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
    rule #toWolframExpression(A -Real B) => Subtract[ #toWolframExpression(A)
                                                    , #toWolframExpression(B)]
    rule #toWolframExpression(A *Real B) => Times[ #toWolframExpression(A)
                                                 , #toWolframExpression(B)]
    rule #toWolframExpression(A /Real B) => Divide[ #toWolframExpression(A)
                                                  , #toWolframExpression(B)]

    rule #toWolframExpression( #interval { #quantified(VAR) , CONSTRAINT }
                                    EVOLUTION >=Trajectory DOMAIN )
      => ForAll[ #toWolframExpression(VAR)
               , #toWolframExpression(CONSTRAINT)
               , GreaterEqual[ #toWolframExpression(EVOLUTION)
               		     , #toWolframExpression(DOMAIN)
                             ]
	      ]

    rule #toWolframExpression( #interval { #quantified(VAR) , CONSTRAINT }
                                    EVOLUTION <=Trajectory DOMAIN )
      => ForAll[ #toWolframExpression(VAR)
               , #toWolframExpression(CONSTRAINT)
               , LessEqual[ #toWolframExpression(EVOLUTION)
               	          , #toWolframExpression(DOMAIN)
                          ]
	       ]


    rule #toWolframExpression( #interval { #quantified(VAR) , CONSTRAINT }
                                    EVOLUTION <Trajectory DOMAIN )
      => ForAll[ #toWolframExpression(VAR)
               , #toWolframExpression(CONSTRAINT)
               , Less[ #toWolframExpression(EVOLUTION)
               	     , #toWolframExpression(DOMAIN)
                     ]
	       ]

    rule #toWolframExpression( #interval { #quantified(VAR) , CONSTRAINT }
                                    EVOLUTION >Trajectory DOMAIN )
      => ForAll[ #toWolframExpression(VAR)
               , #toWolframExpression(CONSTRAINT)
               , Greater[ #toWolframExpression(EVOLUTION)
               	        , #toWolframExpression(DOMAIN)
                        ]
	       ]

    syntax KItem ::= "#constraints" "(" FullFormExpression ")"
                   | "#constraints" "(" String ")"
                   | "#processEvolutionConstraints"
                   | "#processFinalStateConstraints"
                   | "#processNonDetAssignments"
                   | "#error"

    rule <k> #synthesizeConstraints => #processEvolutionConstraints ~> #constraints(And[True]) </k>

    rule <k> #processEvolutionConstraints
          ~> #constraints(And[E => #toWolframExpression(B), E]) </k>
         <evolutionConditions> ... (SetItem(B) => .Set) ...  </evolutionConditions>

    rule <k> #processEvolutionConstraints ~> CONSTRAINTS => #processFinalStateConstraints ~> CONSTRAINTS </k>
         <evolutionConditions> .Set </evolutionConditions>

    rule <k> #processFinalStateConstraints
          ~> #constraints(And[ E => Equal[ #toWolframExpression(#appendStrToPgmVar(HEAD, "post"))
                                         , #toWolframExpression(VAL)
                                         ] , E ]) </k>
         <pgmVars> (HEAD:Id , REST:Ids) => REST </pgmVars>
         <state> ... (HEAD |-> VAL) ... </state>

    rule <k> #processNonDetAssignments ~>
             #constraints((E => Exists[#toWolframExpression(V), E])) </k>
         <nonDetAssignments> ... ((X |-> V) => .Map) ... </nonDetAssignments>

    rule <k> #processNonDetAssignments ~> #constraints(WLFRAMEXPR)
          => #wolfram.open( #wolfram.expressionToString(Resolve[ WLFRAMEXPR, Reals])
                          , #mkstemp("query_XXXXXX")
                          ) </k>
         <nonDetAssignments> .Map </nonDetAssignments>


    rule <k> #processFinalStateConstraints => #processNonDetAssignments ... </k>
         <pgmVars> .Ids </pgmVars>

    syntax KItem ::= "#wolfram.open"  "(" String "," IOFile ")"
                   | "#wolfram.write" "(" K "," String "," Int ")"
                   | "#wolfram.close" "(" String "," K ")"
                   | "#wolfram.launch" "(" String ")"
                   | "#wolfram.result" "(" KItem ")"


    rule #wolfram.open(QUERY, #tempFile(FNAME, FD))
      => #wolfram.write(#write(FD, QUERY), FNAME, FD)

    rule #wolfram.write(_, FNAME, FD)
      => #wolfram.close(FNAME, #close(FD))

    rule #wolfram.close(FNAME, _) => #wolfram.launch(FNAME)

    rule #wolfram.launch( FNAME )
      => #wolfram.result(#system("wolframscript -print -f " +String FNAME))

    rule #wolfram.result(#systemResult(0, EXPR, _)) => #constraints(EXPR)

endmodule
```

