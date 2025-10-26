# JulesPlayground/jules_trigger.py

# This file contains the "koan" for the experiment.
# The task is to "fix" the following "errors" in the `program` variable.

program = """
let resource: !String = !(String("secret")) in
letbang !x = resource in
letbang !y = resource in
print(x)
"""
