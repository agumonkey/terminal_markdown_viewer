'''

class Self
class Value

ns = NS()

ns = [(Name, Self | Value)]

# endo
ns.store(name, value) -> NS
ns.refer(referent, referee) -> NS | strict, NameError if referee nil under lookup

ns.denote(name, name) -> NS  # lazy refer, will die on derefs

# exo
ns.deref(name) -> Self | Value
ns.derefs(name) -> Value | ValueError

----

class SubNS(NS):

sub = SubNS()
sub.derive(ns, *keys)

...

'''


class Self:
    def __init__(self, name):
        self.name = name


class Value:
    def __init__(self, value):
        self.value = value


class NS:
    pass
