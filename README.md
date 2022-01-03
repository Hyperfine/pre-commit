[![Maintained by Hyperfine](https://img.shields.io/badge/maintained%20by-Hyperfine-343B8A.svg)](https://github.com/Hyperfine/)

# Pre-commit hooks

This repo defines Git pre-commit hooks intended for use with [pre-commit](http://pre-commit.com/). The currently
supported hooks are:

* **terraform-fmt**: Rewrites all Terraform configuration files to a canonical format
* **terraform-validate**: Validates all Terraform configuration files
* **packer-validate**: Validates all Packer configuration files
* **tflint**: Linter for Terraform source code
* **terragrunt-hclfmt**: Rewrites all Terragrunt configuration files to a canonical format
* **shellcheck**: Performs linting on bash scripts
* **gofmt**: Gofmt formats Go programs
* **goimports**: Goimports updates imports and formats in the same style as gofmt
* **golint**: Golint is a linter for Go source code
* **yapf**: yapf (Yet Another Python Formatter) is a python formatter from Google
* **helmlint**: Run helm lint, a linter for helm charts
* **markdown-link-check**: Run markdown-link-check to check all the relative and absolute links in markdown docs.
* **check-terratest-skip-env**: Check all go source files for any uncommented os.Setenv calls setting a terratest SKIP environment.
* **conventional-pre-commit**: Checks commit message for Conventional Commits formatting

## General Usage

In each of your repos, add a file called `.pre-commit-config.yaml` with the following contents:

```yaml
repos:
  - repo: https://github.com/Hyperfine/pre-commit
    rev: <VERSION> # Get the latest from: https://github.com/Hyperfine/pre-commit/releases
    hooks:
      - id: terraform-fmt
      - id: terraform-validate
      - id: tflint
      - id: shellcheck
      - id: gofmt
      - id: golint
```

Next, have every developer: 

1. Install [pre-commit](http://pre-commit.com/). E.g. `brew install pre-commit`.
1. Run `pre-commit install` in the repo.

That’s it! Now every time you commit a code change (`.tf` file), the hooks in the `hooks:` config will execute.

## Running Against All Files At Once

### Example: Formatting all files

If you'd like to format all of your code at once (rather than one file at a time), you can run:

```bash
pre-commit run terraform-fmt --all-files
```

### Example: Enforcing in CI

If you'd like to enforce all your hooks, you can configure your CI build to fail if the code doesn't pass checks by
adding the following to your build scripts:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

If all the hooks pass, the last command will exit with an exit code of 0. If any of the hooks make changes (e.g.,
because files are not formatted), the last command will exit with a code of 1, causing the build to fail.

## Helm Lint Caveats

### Detecting charts

The `helmlint` pre-commit hook runs `helm lint` on the charts that have been changed by the commit. It will run once per
changed chart that it detects.

Note that charts are detected by walking up the directory tree of the changed file and looking for a `Chart.yaml` file
that exists on the path.

### linter_values.yaml

`helm lint` requires input values to look for configuration errors in your helm chart. However, this means that the
linter needs a complete values file. Because we want to develop charts that define required values that the operator
should provide, we don't want to specify defaults for all the values the chart expects in the default `values.yaml`
file.

Therefore, to support this, this pre-commit hook looks for a special `linter_values.yaml` file defined in the chart
path. This will be combined with the `values.yaml` file before running `helm lint`. In your charts, you should define
the required values in `linter_values.yaml`.

For example, suppose you had a helm chart that defined two input values: `containerImage` and `containerTag`. Suppose
that your chart required `containerImage` to be defined, but not `containerTag`. To enforce this, you created the
following `values.yaml` file for your chart:

```yaml
# values.yaml

# containerImage is required and defines which image to use

# containerTag specifies the image tag to use. Defaults to latest.
containerTag: latest
```

If you run `helm lint` on this chart, it will fail because somewhere in your chart you will reference
`.Values.containerImage` which will be undefined with this `values.yaml` file. To handle this, you can define a
`linter_values.yaml` file that defines `containerImage`:

```yaml
# linter_values.yaml
containerImage: nginx
```

Now when the pre-commit hook runs, it will call `helm lint` with both `linter_values.yaml` and `values.yaml`:

```shell
helm lint -f values.yaml -f linter_values.yaml .
```

## Shellcheck Arguments

To enable optional shellcheck features you can use the `--enable` flag.
Other shellcheck flags can not be passed through.

```yaml
repos:
  - repo: https://github.com/Hyperfine/pre-commit
    rev: <VERSION>
    hooks:
      - id: shellcheck
        args: ["--enable require-variable-braces,deprecate-which"]
```

## License

This code is released under the Apache 2.0 License. Please see [LICENSE](LICENSE) and [NOTICE](NOTICE) for more details.

Copyright &copy; 2019 Gruntwork, Inc.
Copyright &copy; 2021 Hyperfine, Inc.
