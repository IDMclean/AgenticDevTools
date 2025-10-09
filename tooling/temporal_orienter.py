import os
import datetime
from SPARQLWrapper import SPARQLWrapper, JSON

def get_dbpedia_topic_summary(topic):
    """
    Queries the DBpedia SPARQL endpoint to get the English abstract for a given topic.

    Args:
        topic (str): The DBpedia resource name (e.g., "Software_engineering").

    Returns:
        A string containing the abstract, or an error message.
    """
    endpoint_url = "https://dbpedia.org/sparql"
    query = f"""
    SELECT ?abstract WHERE {{
      <http://dbpedia.org/resource/{topic}> <http://dbpedia.org/ontology/abstract> ?abstract .
      FILTER (lang(?abstract) = 'en')
    }} LIMIT 1
    """
    try:
        sparql = SPARQLWrapper(endpoint_url)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        sparql.setTimeout(15) # Set a 15-second timeout
        results = sparql.query().convert()

        bindings = results.get("results", {}).get("bindings", [])
        if bindings:
            return bindings[0].get("abstract", {}).get("value", "No abstract found.")
        else:
            return f"No abstract found for topic '{topic}'."

    except Exception as e:
        return f"An error occurred during SPARQL query for {topic}: {e}"

def generate_temporal_orientation_report():
    """
    Generates a temporal orientation report by querying DBpedia for key topics
    and saves it to the knowledge core.
    """
    print("--> Generating temporal orientation report from DBpedia...")

    # Topics to query for the orientation report
    topics = {
        "Software Engineering": "Software_engineering",
        "Artificial Intelligence": "Artificial_intelligence",
        "Semantic Web": "Semantic_Web"
    }

    report_content = [
        "# Temporal Orientation Report (via DBpedia)",
        f"**Generated:** {datetime.datetime.now(datetime.timezone.utc).isoformat()}",
        "---",
        "This report provides high-level summaries of key topics from DBpedia to calibrate the agent's knowledge.",
        "---"
    ]

    for display_name, resource_name in topics.items():
        print(f"  - Querying for '{display_name}'...")
        summary = get_dbpedia_topic_summary(resource_name)
        report_content.append(f"## {display_name}\n\n{summary}\n")

    output_dir = "knowledge_core"
    output_path = os.path.join(output_dir, "temporal_orientation.md")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_content))

    print(f"--> Successfully generated temporal orientation report at '{output_path}'")

if __name__ == "__main__":
    generate_temporal_orientation_report()