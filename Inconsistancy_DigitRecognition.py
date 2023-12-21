import os
from rdflib import Graph

# Get the directory of the current script
script_directory = os.path.dirname(__file__)

# Set the current working directory to the directory of the script
os.chdir(script_directory)

# Instantiate graphs and load RDF data
g = Graph()
g2 = Graph()

with open("Rule_DR.n3", "r") as rule_file:
    result = g.parse(file=rule_file, format="text/n3")

with open("KB-DigitRecognition_v2.n3", "r") as kb_file:
    result3 = g2.parse(file=kb_file, format="text/n3")

# Code for extracting individuals from the rule base for KPIs
rule_base_kpis = set()
for row in g.query("""
    SELECT DISTINCT ?KPIs ?allKPIs
    WHERE {
        ?KPIs rdfs:label "KPIs" ;
              owl:oneOf ?list .
        ?list rdf:rest*/rdf:first ?allKPIs .
    }"""):
    rule_base_kpis.add(row['allKPIs'])

# Code for extracting individuals from the rule base for Resources
rule_base_res = set()
for row in g.query("""
    SELECT DISTINCT ?Res ?allRes
    WHERE {
        ?Res rdfs:label "Resources" ;
              owl:oneOf ?list .
        ?list rdf:rest*/rdf:first ?allRes .
    }"""):
    rule_base_res.add(row['allRes'])



# Code for extracting individuals from the knowledge base for prop:hasKPI
knowledge_base_has_kpi = set()
for row in g2.query("""
    SELECT DISTINCT ?process ?subProcess ?kpi
    WHERE {
        {
            ?process a classes:Process ;
                     prop:hasKPI ?kpi .
        }
        UNION
        {
            ?subProcess prop:SubProcess ?process ;
                        prop:hasKPI ?kpi .
        }
    }
"""):
    process = row['process']
    sub_process = row.get('subProcess', None)
    kpi = row['kpi']
    
    if sub_process:
        knowledge_base_has_kpi.add((kpi, sub_process))
    else:
        knowledge_base_has_kpi.add((kpi, process))

# Code for extracting individuals from the knowledge base for prop:hasResourse
knowledge_base_has_resource = set()
for row in g2.query("""
    SELECT DISTINCT ?process ?subProcess ?resource
    WHERE {
        {
            ?process a classes:Process ;
                     prop:hasResourse ?resource .
        }
        UNION
        {
            ?subProcess prop:SubProcess ?process ;
                        prop:hasResourse ?resource .
        }
    }
"""):
    process = row['process']
    sub_process = row.get('subProcess', None)
    resource = row['resource']
    
    if sub_process:
        knowledge_base_has_resource.add((resource, sub_process))
    else:
        knowledge_base_has_resource.add((resource, process))


# Print results of the rule base query for KPIs
print("========== RULE owl:oneof for KPIs =========")
for item in sorted(rule_base_kpis):
    print(item)

# Print results of the rule base query for Res
print("========== RULE owl:oneof for Resources =========")
for item in sorted(rule_base_res):
    print(item)

# Print header for knowledge base query for prop:hasKPI
print("========== KB prop:hasKPI =========")

# Print results of the knowledge base query for prop:hasKPI
for kpi, process in sorted(knowledge_base_has_kpi):
    print(f"{kpi} in individual: {process}")

# Print header for knowledge base query for prop:hasResourse
print("========== KB prop:hasResourse =========")

# Print results of the knowledge base query for prop:hasResourse
for resource, process in knowledge_base_has_resource:
    print(f"{resource} in individual: {process}")

# Extract KPI numbers from the first list
rule_base_kpi_numbers = set(int(kpi.split(':')[-1][3:]) for kpi in rule_base_kpis)

# Extract KPI numbers from the second list
knowledge_base_kpi_numbers = set(int(kpi.split(':')[-1][3:]) for kpi, _ in knowledge_base_has_kpi)

# Identify common and extra KPIs
common_kpis = rule_base_kpi_numbers.intersection(knowledge_base_kpi_numbers)
extra_kpis_in_kb = knowledge_base_kpi_numbers - rule_base_kpi_numbers

# Print the results
print("========== Comparison of KPIs =========")
print("Common KPIs:", sorted(common_kpis))
print("Extra KPIs in KB:", sorted(extra_kpis_in_kb))

# Extract Resource numbers from the first list
rule_base_resource_numbers = set(int(res.split(':')[-1][3:]) for res in rule_base_res)

# Extract Resource numbers from the second list
knowledge_base_resource_numbers = set(int(res.split(':')[-1][3:]) for res, _ in knowledge_base_has_resource)

# Identify common and extra Resources
common_resources = rule_base_resource_numbers.intersection(knowledge_base_resource_numbers)
extra_resources_in_kb = knowledge_base_resource_numbers - rule_base_resource_numbers

# Print the results
print("========== Comparison of Resources =========")
print("Common Resources:", sorted(common_resources))
print("Extra Resources in KB:", sorted(extra_resources_in_kb))