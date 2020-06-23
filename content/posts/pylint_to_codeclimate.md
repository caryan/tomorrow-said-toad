---
title: pylint to CodeClimate converter
date: 2020-06-22
lastmod: 2020-06-22
tags:
  - software
  - python
  - CI
summary: A little helper function to get nice code quality reports in Gitlab
draft: false
---


Gitlab's Code Quality [documentation](https://docs.gitlab.com/ee/user/project/merge_requests/code_quality.html) is all over the place and using the CodeClimate docker images seems to make things more complicated than it needs to be. The [Code Climate Pylint Engine](https://github.com/mercos/codeclimate-pylint) repository (which is what the image uses) gave me a useful starting point but it puts out list of JSON dicts with each issue null-terminated separated (I'm not sure why) and doesn't give a `fingerprint`.

As specified in the [Implementing a custom tool](https://docs.gitlab.com/ee/user/project/merge_requests/code_quality.html#implementing-a-custom-tool) section of the docs Gitlab only needs a small subset of the full [specification](https://github.com/codeclimate/spec/blob/master/SPEC.md) of the codeclimate fields: `description`, `fingerprint`, `location.path`, `location.lines.begin`.

After poking around it seems we can get a very lightweight pylint to Gitlab code quality JSON format by subclassing the `pylint` `JSONReporter` class and then overriding only the `handle_message` method to convert the `pylint` message.

You can then just dump the report to file in your Gitlab CI with `python pylint-to-codeclimate.py owlbear > gl-code-quality-report.json`.

You can find the code in gist: {{<gist caryan 87bdadba4b6579ffed8a87d546364d72>}}
