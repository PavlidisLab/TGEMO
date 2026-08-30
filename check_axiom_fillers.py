#!/usr/bin/env python3
"""Check that every class expression in TGEMO names something the file declares.

Why this exists, since `robot validate-profile --profile Full` passes without it:
an undeclared filler is perfectly legal OWL. It is not legal to Gemma's loader.
A `someValuesFrom` whose target is not a declared class comes back from Jena as a
plain resource rather than a class expression, and reading the restriction throws
-- so the whole class fails to read, not just that one target. On 2026-08-30 that
made all 37 axiom-bearing classes unreadable and the relation rebuild wrote zero
rows, after a full deploy. The file was valid the entire time.

Declarations may be bare. Nothing here asks for a label or a definition: the
owning vocabulary is the authority on what its terms are called, and a copy in
this file would drift from it.

Usage: check_axiom_fillers.py [TGEMO.OWL]
"""
import sys
import xml.etree.ElementTree as ET

OWL = "http://www.w3.org/2002/07/owl#"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RESOURCE = f"{{{RDF}}}resource"
ABOUT = f"{{{RDF}}}about"

# element tag -> what a resource named there must have been declared as
FILLER_TAGS = {
    f"{{{OWL}}}someValuesFrom": "owl:Class",
    f"{{{OWL}}}allValuesFrom": "owl:Class",
    f"{{{OWL}}}onClass": "owl:Class",
    f"{{{OWL}}}onProperty": "owl:ObjectProperty",
}
DECLARES = {
    f"{{{OWL}}}Class": "owl:Class",
    f"{{{OWL}}}ObjectProperty": "owl:ObjectProperty",
    f"{{{OWL}}}DatatypeProperty": "owl:ObjectProperty",   # good enough for onProperty
    f"{{{OWL}}}AnnotationProperty": "owl:ObjectProperty",
}


def main(path):
    root = ET.parse(path).getroot()

    declared = {}
    for el in root.iter():
        kind = DECLARES.get(el.tag)
        uri = el.get(ABOUT)
        if kind and uri:
            declared.setdefault(uri, set()).add(kind)

    problems = []
    for el in root.iter():
        want = FILLER_TAGS.get(el.tag)
        uri = el.get(RESOURCE)
        if not want or not uri:
            continue          # an anonymous (nested) filler declares nothing to check
        if want not in declared.get(uri, set()):
            problems.append((el.tag.split("}")[-1], uri, want))

    if problems:
        print(f"{len(problems)} class expression(s) name something this file does not declare.")
        print("Gemma cannot read the classes carrying them; add a bare declaration for each.\n")
        for tag, uri, want in sorted(set(problems)):
            print(f"  {tag} -> {uri}")
            print(f'      needs: <{want} rdf:about="{uri}"/>')
        return 1

    checked = sum(1 for el in root.iter() if el.tag in FILLER_TAGS and el.get(RESOURCE))
    print(f"OK: {checked} class-expression references, all declared.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "TGEMO.OWL"))
