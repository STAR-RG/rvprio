"""
Runtime Verification Priorizator
Usage: rvprio [options]

  -h --help         Show this screen.
  -k --kernel=rv    Violations to look for [default: javamop]
  -i --input=file   Input file.
"""
import cerberus
import docopt

import rvprio.filesystem
import rvprio.kernels.javamop
import rvprio.plugins.method_analyzer
import rvprio.validator


def main(kernel, input, **kwargs):
    """ Main function for rvprio. """
    kernel = rvprio.kernels.javamop.JavaMOP(input_file=input)
    violations = kernel.get_violations()

    filesystem = rvprio.filesystem.Filesystem(violations)
    found_violations = filesystem.find_sources()

    final_violations = list()
    for violation in found_violations:
        final_violation = rvprio.models.RVprioViolation(violation)

        subpath = violation.file_name
        path = str(filesystem.find_file(subpath)[0])
        line = violation.line

        metadata = rvprio.plugins.method_analyzer.get_metadata(path, line)

        if metadata:
            final_violation.add_plugin_info(metadata)
            final_violations.append(final_violation)


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__, version="beta")
    cli_validator = cerberus.Validator(rvprio.validator.CLI_SCHEMA)
    is_valid = cli_validator.validate(arguments)
    if is_valid:
        arguments = {k.strip("--"): v for (k, v) in arguments.items()}
        main(**arguments)
