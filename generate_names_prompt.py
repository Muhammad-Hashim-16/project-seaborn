"""
generate_names_prompt.py — SeabornGallery AI Tag Generator & Merger
====================================================================

This script has two modes:

1. GENERATE PROMPTS (default):
   Reads data.json and code snippets, groups plots into batches of 10,
   and generates AI prompts that the user can paste into any chatbot
   to get tag suggestions back.

   Usage:   python generate_names_prompt.py
   Output:  naming_prompts.txt

2. MERGE AI RESPONSES:
   Run with --merge flag. Reads data.json and ai_responses.json (where
   you paste all AI tag responses combined into one JSON array) and
   merges only the tags into data.json.

   Usage:   python generate_names_prompt.py --merge
   Input:   ai_responses.json
   Output:  data.json (updated in-place)
"""

import json
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Allowed tags (whitelist)
# ---------------------------------------------------------------------------

ALLOWED_TAGS = [
    "Line", "Bar", "Scatter", "Histogram", "KDE", "Pie", "Heatmap",
    "Statistical", "Boxplot", "Violin", "Regression", "Distribution",
    "Categorical", "Relational", "Time Series", "Multi-plot", "Pairplot",
    "Jointplot", "Facet", "Strip", "Swarm", "Point", "Count", "ECDF",
    "Rug", "Cluster", "Correlation", "Residual", "Polynomial", "Logistic",
    "Color Palette", "Annotation", "Multi-axis", "Error Bars", "Bubble",
    "Filled", "Stepped", "Grouped", "Stacked", "Matrix",
]

ALLOWED_TAGS_SET = set(ALLOWED_TAGS)


# ---------------------------------------------------------------------------
# Mode 1 — Generate prompts
# ---------------------------------------------------------------------------

def generate_prompts() -> None:
    """Read data.json and code snippets, generate AI prompts in batches of 10."""
    data_path = Path("data.json")
    if not data_path.exists():
        print("ERROR: data.json not found. Run splitter.py first.")
        return

    data = json.loads(data_path.read_text(encoding='utf-8'))
    if not data:
        print("ERROR: data.json is empty. Run splitter.py first.")
        return

    print(f"Loaded {len(data)} plots from data.json")

    # Group into batches of 10
    batch_size = 10
    batches = []
    for i in range(0, len(data), batch_size):
        batches.append(data[i:i + batch_size])

    all_prompts = []

    for batch_idx, batch in enumerate(batches, 1):
        prompt_lines = []
        prompt_lines.append(f"--- BATCH {batch_idx} of {len(batches)} ---\n")
        prompt_lines.append(
            "You are analyzing Python seaborn visualization code snippets. "
            "For each plot below, provide ONLY the tags — the name and difficulty "
            "are already known.\n"
        )
        prompt_lines.append("Tags must come from this list ONLY:")
        prompt_lines.append(json.dumps(ALLOWED_TAGS) + "\n")
        prompt_lines.append("Pick minimum 1, maximum 4 tags per plot.\n")
        prompt_lines.append(
            "Return ONLY a raw JSON array, no explanation, no markdown:"
        )
        prompt_lines.append("[")
        for j, plot in enumerate(batch):
            comma = "," if j < len(batch) - 1 else ""
            example_tags = '["Tag1", "Tag2"]'
            prompt_lines.append(
                f'  {{"id": {plot["id"]}, "tags": {example_tags}}}{comma}'
            )
        prompt_lines.append("]\n")
        prompt_lines.append("Here are the plots:\n")

        for plot in batch:
            code_path = Path("code_snippets") / f"{plot['id']}.txt"
            if code_path.exists():
                code = code_path.read_text(encoding='utf-8')
            else:
                code = "# Code file not found"

            prompt_lines.append(
                f"--- Plot {plot['id']}: {plot['name']} ({plot['difficulty']}) ---"
            )
            prompt_lines.append(code)
            prompt_lines.append("")

        prompt_lines.append("---\n")
        all_prompts.append("\n".join(prompt_lines))

    # Write all prompts to naming_prompts.txt
    output_path = Path("naming_prompts.txt")
    output_path.write_text(
        "\n\n" + "=" * 70 + "\n\n".join(all_prompts),
        encoding='utf-8',
    )

    print(f"Generated {len(batches)} batch prompts in naming_prompts.txt")
    print(f"\nInstructions:")
    print(f"  1. Open naming_prompts.txt")
    print(f"  2. Copy each batch prompt and paste it into any AI chatbot")
    print(f"  3. Collect all JSON array responses")
    print(f"  4. Combine them into a single JSON array in ai_responses.json")
    print(f"  5. Run: python generate_names_prompt.py --merge")


# ---------------------------------------------------------------------------
# Mode 2 — Merge AI responses
# ---------------------------------------------------------------------------

def merge_responses() -> None:
    """Read ai_responses.json and merge tags into data.json."""
    data_path = Path("data.json")
    responses_path = Path("ai_responses.json")

    if not data_path.exists():
        print("ERROR: data.json not found. Run splitter.py first.")
        return

    if not responses_path.exists():
        print("ERROR: ai_responses.json not found.")
        print("  Create this file by combining all AI tag responses into")
        print("  a single JSON array, e.g.:")
        print('  [{"id": 1, "tags": ["Scatter", "Relational"]}, ...]')
        return

    data = json.loads(data_path.read_text(encoding='utf-8'))
    responses = json.loads(responses_path.read_text(encoding='utf-8'))

    if not isinstance(responses, list):
        print("ERROR: ai_responses.json must contain a JSON array.")
        return

    # Build lookup by id
    data_lookup = {entry['id']: entry for entry in data}

    updated_count = 0
    invalid_tags = []

    for response in responses:
        plot_id = response.get('id')
        tags = response.get('tags', [])

        if plot_id is None:
            print(f"  WARNING: Entry missing 'id' field: {response}")
            continue

        if plot_id not in data_lookup:
            print(f"  WARNING: Plot id {plot_id} not found in data.json, skipping.")
            continue

        # Validate tags against allowed list
        valid_tags = []
        for tag in tags:
            if tag in ALLOWED_TAGS_SET:
                valid_tags.append(tag)
            else:
                invalid_tags.append((plot_id, tag))
                print(f"  WARNING: Invalid tag '{tag}' for plot {plot_id}, skipping tag.")

        data_lookup[plot_id]['tags'] = valid_tags
        updated_count += 1

    # Write updated data.json
    updated_data = sorted(data_lookup.values(), key=lambda x: x['id'])
    data_path.write_text(
        json.dumps(updated_data, indent=2, ensure_ascii=False),
        encoding='utf-8',
    )

    print(f"\nMerge complete:")
    print(f"  Updated: {updated_count} entries")
    print(f"  Invalid tags found: {len(invalid_tags)}")
    if invalid_tags:
        for pid, tag in invalid_tags:
            print(f"    Plot {pid}: '{tag}'")
    print(f"  Saved: data.json")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if "--merge" in sys.argv:
        print("=" * 50)
        print("  SeabornGallery — Merge AI Tag Responses")
        print("=" * 50)
        merge_responses()
    else:
        print("=" * 50)
        print("  SeabornGallery — Generate AI Tag Prompts")
        print("=" * 50)
        generate_prompts()
