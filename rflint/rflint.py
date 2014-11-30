"""
rflint - a lint-like tool for robot framework plain text files

Copyright 2014 Bryan Oakley

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import os
import sys
import glob
import argparse
import imp

from .common import SuiteRule, TestRule, KeywordRule, GeneralRule, Rule, ERROR, WARNING
from parser import RobotFile


class RfLint(object):
    """Robot Framework Linter"""

    def __init__(self):
        here = os.path.abspath(os.path.dirname(__file__))
        builtin_rules = os.path.join(here, "rules")
        site_rules = os.path.join(here, "site-rules")
        for path in (builtin_rules, site_rules):
            for filename in glob.glob(path+"/*.py"):
                if filename.endswith(".__init__.py"):
                    continue
                basename = os.path.basename(filename)
                (name, ext) = os.path.splitext(basename)
                imp.load_source(name, filename)

    def run(self, args):
        """Parse command line arguments, and run rflint"""

        self.args = self.parse_and_process_args(args)

        self.suite_rules = self._get_rules(SuiteRule)
        self.testcase_rules = self._get_rules(TestRule)
        self.keyword_rules = self._get_rules(KeywordRule)
        self.general_rules = self._get_rules(GeneralRule)
                
        if self.args.list:
            self.list_rules()
            sys.exit(0)
        
        all_rules = [repr(x) for x in self.suite_rules] + \
                    [repr(x) for x in self.testcase_rules] + \
                    [repr(x) for x in self.keyword_rules] + \
                    [repr(x) for x in self.general_rules] 

        for filename in self.args.args:
            if not (self.args.no_filenames):
                print "+ "+filename
            suite = RobotFile(filename)
            for rule in self.suite_rules:
                rule.apply(suite)
            for testcase in suite.testcases:
                for rule in self.testcase_rules:
                    rule.apply(testcase)
            for keyword in suite.keywords:
                for rule in self.keyword_rules:
                    rule.apply(keyword)

    def list_rules(self):
        """Print a list of all rules"""
        all_rules = [repr(x) for x in self.suite_rules] + \
                    [repr(x) for x in self.testcase_rules] + \
                    [repr(x) for x in self.keyword_rules] + \
                    [repr(x) for x in self.general_rules] 

        print "\n".join(sorted([repr(x) for x in all_rules], 
                               key=lambda s: s[2:]))

    def _get_rules(self, cls):
        """Returns a list of rules of a given class"""
        result = []
        for rule_class in cls.__subclasses__():
            rule_name = rule_class.__name__.lower()

            if ("all" in self.args.ignore and
                (rule_name not in self.args.warn and
                 rule_name not in self.args.error)):
                # if we are told to ignore all, skip this one unless
                # it was explicitly added with --ignore or --warn
                continue

            if ((rule_name in self.args.ignore)):
                # if the user asked this rule to be ignored, skip it
                continue

            # if the rule was an option to --warn or --error, update
            # the rule's severity
            if rule_name in self.args.warn:
                rule_class.severity = WARNING
            elif rule_name in self.args.error:
                rule_class.severity = ERROR

            # create an instance of the rule, and add it
            # to the list of result
            result.append(rule_class())

        return result

    def parse_and_process_args(self, args):
        """Handle the parsing of command line arguments."""

        parser = argparse.ArgumentParser(
            description="A style checker for robot framework plain text files",
            epilog="You can use 'all' in place of RuleName to refer to all rules. " + \
                "For example: '--ignore all --warn DuplicateTestNames' will ignore all rules " + \
                "except DuplicateTestNames."
            )
        parser.add_argument("--error", "-e", metavar="RuleName", action="append")
        parser.add_argument("--ignore", "-i", metavar="RuleName", action="append")
        parser.add_argument("--warn", "-w", metavar="RuleName", action="append")
        parser.add_argument("--list", "-l", action="store_true")
        parser.add_argument("--no-filenames", action="store_true")
        parser.add_argument("--format", "-f")
        parser.add_argument('args', metavar="filenames", nargs=argparse.REMAINDER)

        args = parser.parse_args(args)
        args.ignore = [rule.lower() for rule in args.ignore] if args.ignore else []
        args.warn = [rule.lower() for rule in args.warn] if args.warn else []
        args.error = [rule.lower() for rule in args.error] if args.error else []

        output_format = "{severity}: {linenumber}, {char}: {message} ({rulename})"

        if args.format is not None:
            Rule.output_format = args.format

        return args

        