from kninja import *
from kninja.runner import KRunner
import copy
import functools
import subprocess
import re
import sys

# Customize KDefinition For Hybrid Program Semantics
# ==============================================

class KHPDefinition(KDefinition):

    def synthesis(self, expected = None, inputs = [], implicit_inputs = [], glob = None, alias = None, default = True, flags = ''):
        if glob is not None:
            inputs += glob_module.glob(glob)
        ret = []
        for input in inputs:
            e = expected
            if e is None:
                e = append_extension(input, 'cond.expected')
            input = self.proj.to_target(input)
            test = input.then(self.runner_script(mode = 'synthesis', flags = flags).implicit(implicit_inputs)) \
                        .then(self.proj.check(expected = e))
            if default: test.default()
            ret += [test]
        if alias is not None:
            ret = self.proj.alias(alias, ret)
        return ret


class KHPProject(KProject):

    def definition( self
                  , alias
                  , backend
                  , main
                  , runner_script
                  , other = []
                  , directory = None
                  , tangle_selector = '.k'
                  , flags = ''
                  ):
        if directory is None:
            directory = self.builddir('defn', alias)

        # If a source file has extension '.md', tangle it:
        def target_from_source(source):
            source = self.to_target(source)
            assert(type(source) == Target)
            source = self.tangle_if_markdown( source
                                            , selector  = tangle_selector
                                            , directory = directory
                                            )
            return source
        main = target_from_source(main)
        other = map(target_from_source, other)

        kompiled_dir =  os.path.join(directory, basename_no_ext(main.path) + '-kompiled')
        output = None
        env = ''
        implicit_inputs = [self.build_k(backend)]
        if backend == 'ocaml':
            output = os.path.join(kompiled_dir, 'interpreter')
            implicit_inputs += [self.configure_opam()]
            env = 'opam config exec --'
        elif backend == 'llvm':
            output = os.path.join(kompiled_dir, 'interpreter')
        elif backend == 'java':
            output = os.path.join(kompiled_dir, 'timestamp')
        elif backend == 'haskell':
            output = os.path.join(kompiled_dir, 'definition.kore')
        else:
            assert false, 'Unknown backend "' + backend + "'"

        target = main.then(self.rule_kompile()                    \
                               .output(output)                    \
                               .implicit(other)                   \
                               .implicit(implicit_inputs) \
                               .variable('backend', backend)      \
                               .variable('directory', directory)  \
                               .variable('env', env)              \
                               .variable('flags', '-I ' + directory + ' ' + flags)  \
                          ).alias(alias)

        return KHPDefinition( self, alias, directory, kompiled_dir, target
                            , runner_script = runner_script
                            , krun_extension = alias + '-krun', krun_env = env
                            , kprove_extension = alias + '-kprove'
                            , backend = backend
                            )


# Customize KRunner For Hybrid Program Semantics
# ==============================================

class KHPRunner(KRunner):

    def __init__(self, proj, default_definition = None):
        self.parser = argparse.ArgumentParser()
        self.proj = proj
        parser = self.parser
        self.default_definition = default_definition

        parser.add_argument('--opamswitch', default = '4.06.1+k')

        subparsers = parser.add_subparsers()

        kast_parser = subparsers.add_parser('kast', help = 'Run a program against a definition')
        self.add_definition_argument(kast_parser)
        kast_parser.add_argument('program', help = 'Path to program')
        kast_parser.add_argument('args', nargs = argparse.REMAINDER, help = 'Arguments to pass to K')
        kast_parser.set_defaults(func = functools.partial(self.execute_kast, self))

        run_parser = subparsers.add_parser('run', help = 'Run a program against a definition')
        self.add_definition_argument(run_parser)
        run_parser.add_argument('program', help = 'Path to program')
        run_parser.add_argument('args', nargs = argparse.REMAINDER, help = 'Arguments to pass to K')
        run_parser.set_defaults(func = functools.partial(self.execute_krun, self))

        prove_parser = subparsers.add_parser('prove', help = 'Use KProve to check a specification')
        self.add_definition_argument(prove_parser)
        prove_parser.add_argument('specification', help = 'Path to spec')
        prove_parser.add_argument('args', nargs = argparse.REMAINDER, help = 'Arguments to pass to K')
        prove_parser.set_defaults(func = functools.partial(self.execute_kprove, self))

        synthesis_parser = subparsers.add_parser('synthesis', help = 'Use Symbolic Execution to Synthesize Constraints')
        self.add_definition_argument(synthesis_parser)
        synthesis_parser.add_argument('program', help = 'Path to program')
        synthesis_parser.add_argument('args', nargs = argparse.REMAINDER, help = 'Arguments to pass to K')
        synthesis_parser.set_defaults(func = functools.partial(self.execute_synthesis, self))

    def execute_synthesis(self, args):
        definition = self.proj._k_definitions[args.definition]
        binary = self.proj.kbindir('krun')
        process_args = []
        opam_config_exec = []
        if definition.backend == 'ocaml':
            opam_config_exec = ['opam', 'config', 'exec', '--']
            binary = 'opam'
        process_args =  opam_config_exec \
                      + [ self.proj.kbindir('krun') \
                        , '--directory', definition.directory()
                        , args.program
                        , '-cMODE=\"#constraintSynthesis\"'] \
                      + self.proj._k_definitions[args.definition]._krun_flags.split() \
                      + args.args
        result = subprocess.run( process_args
                               , stdout = subprocess.PIPE
                               , stderr = subprocess.PIPE
                               , check = True)
        if(result.returncode == 0):
            pattern = re.compile(r'#constraints\s*\(\s*\"(.*).*\"\s*\)', re.DOTALL)
            matches = re.search(pattern, str(result.stdout))
            if matches == None:
                print(result.stdout, file = sys.stderr)
                sys.exit(1)
            else:
                output = matches.group(1)
                output = re.sub(r'\\\\n$', '', output) #weird newline at end
                print(output)
        else:
                print(result.stderr, file = sys.stderr)
                sys.exit(result.returncode)
