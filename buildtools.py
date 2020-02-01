from kninja import *

# Customize KDefinition For Hybrid Program Semantics
# ==============================================

class KHPDefinition(KDefinition):

    def synthesis(self, inputs = [], glob = None, alias = None, default = True, expected = None, flags = '', tangle_selector = '.k'):
        if glob is not None:
            inputs += glob_module.glob(glob)
        ret = []
        for input in inputs:
            e = expected
            if e is None:
                e = append_extension(input, 'expected')
            input = self.proj.to_target(input)
            test = input.then(self.runner_script(mode = 'synthesis', flags = flags).implicit(implicit_inputs)) \
                        .then(self.proj.check(expected = e))
            if default: test.default()
            ret += [test]
        if alias is not None:
            ret = self.proj.alias(alias, ret)
        return ret


class KHPProject(KProject):

    def definition(self, *args, **kwargs):
        kdefinition = super().definition(*args, **kwargs)
        khp_kdefinition = copy.copy(kdefinition)
        khp_kdefinition.__class__ = KHPDefinition
        return khp_kdefinition


# Customize KRunner For Hybrid Program Semantics
# ==============================================

class KHPRunner(KRunner):
    def __init__(self, proj, default_definition = None):
        super().__init(proj, default_definition)
        subparser = self.parser.add_subparsers()

        synthesis_parser = subparsers.add_parser('synthesis', help = 'Use Symbolic Execution to Synthesize Constraints')
        self.add_definition_argument(synthesis_parser)
        synthesis_parser.add_argument('program', help = 'Path to program')
        synthesis_parser.add_argument('args', nargs = argparse.REMAINDER, help = 'Arguments to pass to K')
        synthesis_parser.set_defaults(func = functools.partial(self.execute_synthesis, self))

    def execute_synthesis(self, args):
        definition = self.proj._k_definitions[args.definition]
        binary = self.proj.kbindir('krun')
        opam_config_exec = []
        if definition.backend == 'ocaml':
            opam_config_exec = ['opam', 'config', 'exec', '--']
            binary = 'opam'
        subprocess.run( binary
                      , *opam_config_exec
                      , self.proj.kbindir('krun')
                      , '--directory', definition.directory()
                      , args.program
                      , '-cMODE=\"#constraintSynthesis\"'
                      , *self.proj._k_definitions[args.definition]._krun_flags.split()
                      , *args.args
                      , capture_ouput = False
                      , check = True
                      )

