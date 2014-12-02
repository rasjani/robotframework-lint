*** Settings ***
| Documentation
| ... | This suite includes some very basic smoke tests for rflint
| # 
| Library    | OperatingSystem
| Library    | Process
| Library    | SharedKeywords.py
| Resource   | SharedKeywords.robot
| Force Tags | smoke

*** Test Cases ***
| Command line help 
| | [Documentation]
| | ... | This test verifies that --help returns some useful information
| | ... | 
| | ... | Not exactly an exhaustive test, but it at least
| | ... | verifies that the command works. 
| | 
| | Run rf-lint with the following options:
| | ... | --help
| | 
| | rflint return code should be | 0
| | # instead of doing an exhaustive test, let's just make 
| | # a quick spot-check
| | Output should contain
| | ... | usage:*
| | ... | optional arguments:
| | ... | *-h, --help*
| | ... | *--error <RuleName>, -e <RuleName>*
| | ... | *--ignore <RuleName>, -i <RuleName>*
| | ... | *--warn <RuleName>, -w <RuleName>*
| | ... | *--list*
| | ... | *--no-filenames*
| | ... | *--format FORMAT, -f FORMAT*

| | log | STDOUT:\n${result.stdout}
| | log | STDERR:\n${result.stderr}

| --list option
| | [Documentation]
| | ... | Verify that the --list option works.
| | 
| | Run rf-lint with the following options:
| | ... | --list
| | rflint return code should be | 0
| | log | STDOUT:\n${result.stdout}
| | log | STDERR:\n${result.stderr}

| rflint smoke.robot
| | [Documentation]
| | ... | Run rflint against this test suite
| | 
| | Run rf-lint with the following options:
| | ... | --format | {severity}: {linenumber}, {char}: {message} ({rulename})
| | ... | --no-filenames
| | ... | ${SUITE_SOURCE}
| | rflint return code should be | 0
| | rflint should report 0 errors
| | rflint should report 0 warnings

| smoke.tsv
| | [Documentation]
| | ... | Run rflint against this file in .tsv format
| | [Setup] | Convert ${SUITE_SOURCE} to .tsv
| | Run rf-lint with the following options: | ${TEMPDIR}/smoke.tsv
| | rflint return code should be | 0
| | rflint should report 0 errors
| | rflint should report 0 warnings
| | [Teardown] | Run keyword if | ${result.rc} == 0 | Remove file | ${TEMPDIR}/smoke.tsv

| smoke.txt (spaces, not pipes or tabs)
| | [Documentation] 
| | ... | Run rflint against this file in space separated format
| | [Setup] | Convert ${SUITE_SOURCE} to .txt
| | run rf-lint with the following options: | ${TEMPDIR}/smoke.txt
| | rflint return code should be | 0
| | rflint should report 0 errors
| | rflint should report 0 warnings
| | [Teardown] | Run keyword if | ${result.rc} == 0 
| | ... | Remove file | ${TEMPDIR}/smoke.txt

| non-zero exit code on failure
| | [Documentation]
| | ... | Validates that exit code is non-zero if errors are present
| | 
| | [Setup] | Create a test suite | ${TEMPDIR}/busted.robot
| | ... | *** Test Cases ***\n
| | ... | An example test case\n
| | ... | | # no documentation
| | ... | | log | hello world
| | 
| | Run rf-lint with the following options: 
| | ... | --warn | RequireSuiteDocumentation
| | ... | --error | RequireTestDocumentation
| | ... | ${TEMPDIR}/busted.robot
| | 
| | # there should be two errors: no suite documentation, no testcase documentation
| | # but the return code is only a count of the errors
| | rflint return code should be | 1
| | rflint should report 1 errors
| | rflint should report 1 warnings
| | 
| | [Teardown] | Run keyword if | ${result.rc} == 1 
| | ... | Remove file | ${TEMPDIR}/busted.robot

*** Keywords ***
| Convert ${path} to ${format}
| | [Documentation]
| | ... | Converts this file to the given format, and save it to \${TEMPDIR}
| | ... | Note: a type of .txt will be saved in the space-sepraated format.
| | ... | 
| | ... | Example:
| | ... | 
| | ... | Convert smoke.robot to .txt
| | 
| | ${python}= | Evaluate | sys.executable | sys | # use same python used to run the tests
| | ${outfile}= | Set variable | ${TEMPDIR}/smoke${format}
| | ${result}= | Run process 
| | ... | ${python} | -m | robot.tidy | ${SUITE_SOURCE} | ${outfile}
| | log | saving file as ${outfile} | DEBUG
| | [return] | ${result}