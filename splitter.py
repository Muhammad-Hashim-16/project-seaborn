"""
splitter.py — SeabornGallery Plot Splitter
==========================================

Parses src/master_plots.py, splits it into individual plot code blocks,
executes each plot to generate PNG figures, and creates data.json for the
web gallery frontend.

Usage:
    python splitter.py

Run this script from the project root directory (where this file lives).
It expects src/master_plots.py to exist and contain plot markers in the
format: # 1 Scatter Plot, # 2 Line Plot, etc.

Outputs:
    figures/          — One PNG per plot (1.png, 2.png, ...)
    code_snippets/    — One TXT per plot (1.txt, 2.txt, ...)
    data.json         — Metadata array for the web frontend
    failed_plots.json — Details of any plots that failed to execute
"""

# === CRITICAL: Set Agg backend BEFORE any other matplotlib import ===
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import re
import json
import traceback
from pathlib import Path

# ---------------------------------------------------------------------------
# ANSI color helpers
# ---------------------------------------------------------------------------

class Colors:
    """ANSI escape codes for colored terminal output."""
    RESET   = '\033[0m'
    BOLD    = '\033[1m'
    RED     = '\033[91m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    CYAN    = '\033[96m'
    MAGENTA = '\033[95m'
    DIM     = '\033[2m'


def log_info(msg: str) -> None:
    """Print an informational message in cyan."""
    print(f"{Colors.CYAN}[INFO]{Colors.RESET}  {msg}")


def log_success(msg: str) -> None:
    """Print a success message in green."""
    print(f"{Colors.GREEN}[OK]{Colors.RESET}    {msg}")


def log_warn(msg: str) -> None:
    """Print a warning message in yellow."""
    print(f"{Colors.YELLOW}[WARN]{Colors.RESET}  {msg}")


def log_error(msg: str) -> None:
    """Print an error message in red."""
    print(f"{Colors.RED}[FAIL]{Colors.RESET}  {msg}")


def log_header(msg: str) -> None:
    """Print a bold header message."""
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}{Colors.RESET}\n")


# ---------------------------------------------------------------------------
# Step 1 — Setup directories
# ---------------------------------------------------------------------------

def setup_directories() -> None:
    """Create figures/ and code_snippets/ folders if they do not exist."""
    for folder in [Path("figures"), Path("code_snippets")]:
        folder.mkdir(parents=True, exist_ok=True)
        log_info(f"Directory ready: {folder}/")


# ---------------------------------------------------------------------------
# Step 2 — Parse the master file
# ---------------------------------------------------------------------------

def read_master_file(path: Path) -> str:
    """Read the master_plots.py file and return its content as a string."""
    if not path.exists():
        raise FileNotFoundError(
            f"\n{Colors.RED}ERROR:{Colors.RESET} Could not find '{path}'.\n"
            f"  Make sure you have placed your master_plots.py file inside\n"
            f"  the src/ folder before running this script.\n"
            f"  Expected path: {path.resolve()}"
        )
    return path.read_text(encoding='utf-8')


def find_phase_headers(content: str) -> list[tuple[int, int]]:
    """
    Find all PHASE header lines and return a list of (char_position, phase_number).
    A phase header matches: # PHASE N  (case-insensitive).
    """
    phase_pattern = re.compile(r'#\s*PHASE\s*(\d+)', re.IGNORECASE)
    phases = []
    for match in phase_pattern.finditer(content):
        phase_num = int(match.group(1))
        char_pos = match.start()
        phases.append((char_pos, phase_num))
    return phases


def determine_difficulty(plot_char_pos: int, phase_headers: list[tuple[int, int]]) -> str:
    """
    Determine difficulty for a plot based on which PHASE header appears
    most recently before its position in the file.
    """
    current_phase = 0  # default: no phase found
    for header_pos, phase_num in phase_headers:
        if header_pos < plot_char_pos:
            current_phase = phase_num
        else:
            break

    difficulty_map = {
        1: "Beginner",
        2: "Intermediate",
        3: "Advanced",
    }
    return difficulty_map.get(current_phase, "Beginner")


def find_plot_markers(content: str) -> list[dict]:
    """
    Find all plot marker lines in the content.

    A valid plot marker matches: ^# (\\d+) (.+)$
    Additional validation:
    - The character after the number must be a space (not a dot or colon)
    - The number must be between 1 and 999

    Returns a list of dicts with keys: number, name, char_pos
    """
    plot_marker_pattern = re.compile(r'^# (\d+) (.+)$', re.MULTILINE)
    markers = []

    for match in plot_marker_pattern.finditer(content):
        full_line = match.group(0)
        num_str = match.group(1)
        name_text = match.group(2)
        number = int(num_str)

        # Validate: number must be 1-999
        if number < 1 or number > 999:
            continue

        # Validate: the character after the number in the original line
        # must be a space (not a dot, not a colon).
        # The pattern is "# <number><char>..." — check char after the number
        prefix = f"# {num_str}"
        rest_of_line = full_line[len(prefix):]
        if rest_of_line and rest_of_line[0] == '.':
            continue  # Skip lines like "# 1. MODULE IMPORTS"

        # Clean up name: strip whitespace, remove trailing colon
        name = name_text.strip().rstrip(':').strip()

        markers.append({
            'number': number,
            'name': name,
            'char_pos': match.start(),
            'match_end': match.end(),
        })

    return markers


def extract_setup_block(content: str, first_marker_pos: int) -> str:
    """
    Extract everything from the top of the file up to (but not including)
    the first plot marker line. This is the setup block containing imports,
    rcParams, dataset loading, etc.
    """
    setup = content[:first_marker_pos].rstrip('\n').rstrip('\r')
    return setup


def extract_code_blocks(content: str, markers: list[dict]) -> dict[int, str]:
    """
    Split the file content at each plot marker to extract each plot's code block.
    The code block for plot N is everything between the marker line and the next
    marker (or end of file), NOT including the marker line itself.
    """
    code_blocks = {}

    for i, marker in enumerate(markers):
        # Start right after the marker line
        start = marker['match_end']

        # End at the next marker's char_pos, or end of file
        if i + 1 < len(markers):
            end = markers[i + 1]['char_pos']
        else:
            end = len(content)

        block = content[start:end]

        # Strip leading/trailing blank lines
        lines = block.split('\n')
        # Remove leading blank lines
        while lines and lines[0].strip() == '':
            lines.pop(0)
        # Remove trailing blank lines
        while lines and lines[-1].strip() == '':
            lines.pop()

        code_blocks[marker['number']] = '\n'.join(lines)

    return code_blocks


# ---------------------------------------------------------------------------
# Step 3 — Save code snippets
# ---------------------------------------------------------------------------

def save_code_snippets(code_blocks: dict[int, str]) -> None:
    """Save each plot's raw code block to code_snippets/N.txt."""
    for num, code in code_blocks.items():
        path = Path("code_snippets") / f"{num}.txt"
        path.write_text(code, encoding='utf-8')
    log_success(f"Saved {len(code_blocks)} code snippets to code_snippets/")


# ---------------------------------------------------------------------------
# Step 4 — Execute plots and save figures
# ---------------------------------------------------------------------------

def inject_savefig(code_block: str, plot_num: int) -> str:
    """
    Insert a savefig() call immediately before the plt.close() line
    in the code block. Handles both fig_N and g_N.fig patterns.

    Returns the modified code block string.
    """
    save_instruction = f'fig_{plot_num}.savefig("figures/{plot_num}.png", dpi=150, bbox_inches="tight")'

    lines = code_block.split('\n')
    close_index = None

    # Find the line containing plt.close(
    for idx, line in enumerate(lines):
        if 'plt.close(' in line:
            close_index = idx
            break

    if close_index is not None:
        # Check if the code uses a grid/joint/pair object (g_N) with g_N.fig
        # If so, use g_N.fig for savefig instead of fig_N
        fig_var = f'fig_{plot_num}'
        grid_var = f'g_{plot_num}'

        # Check if g_N exists in the code block (figure-level seaborn plots)
        if grid_var in code_block and f'{grid_var}.fig' in code_block:
            save_instruction = f'{grid_var}.fig.savefig("figures/{plot_num}.png", dpi=150, bbox_inches="tight")'
        elif fig_var not in code_block and grid_var in code_block:
            # g_N exists but no g_N.fig reference — try g_N.fig anyway
            save_instruction = f'{grid_var}.fig.savefig("figures/{plot_num}.png", dpi=150, bbox_inches="tight")'

        # Determine indentation from the plt.close line
        indent = ''
        stripped = lines[close_index].lstrip()
        if len(stripped) < len(lines[close_index]):
            indent = lines[close_index][:len(lines[close_index]) - len(stripped)]

        lines.insert(close_index, indent + save_instruction)

    return '\n'.join(lines)


def execute_plots(
    setup_block: str,
    code_blocks: dict[int, str],
    markers: list[dict],
) -> tuple[list[dict], list[dict]]:
    """
    Execute the setup block once, then execute each plot's code block
    in a shared namespace. Returns (successful_plots, failed_plots).
    """
    namespace: dict = {}

    # Execute setup block first
    log_info("Executing setup block (imports, datasets, configuration)...")
    try:
        exec(setup_block, namespace)
        log_success("Setup block executed successfully.")
    except Exception as e:
        log_error(f"Setup block failed: {e}")
        log_error("Cannot continue without setup. Aborting.")
        raise

    successful = []
    failed = []

    # Build a lookup from marker number to marker info
    marker_lookup = {m['number']: m for m in markers}

    # Process plots in ascending order
    sorted_nums = sorted(code_blocks.keys())

    for plot_num in sorted_nums:
        code = code_blocks[plot_num]
        marker_info = marker_lookup.get(plot_num, {})
        plot_name = marker_info.get('name', f'Plot {plot_num}')

        try:
            # Inject savefig before plt.close
            modified_code = inject_savefig(code, plot_num)

            # Execute the modified code in shared namespace
            exec(modified_code, namespace)

            # Clean up any remaining figures
            exec('import matplotlib.pyplot as _plt; _plt.close("all")', namespace)

            # Verify figure was saved
            fig_path = Path("figures") / f"{plot_num}.png"
            if fig_path.exists():
                log_success(f"Plot {plot_num:>3}: {plot_name}")
                successful.append(marker_info)
            else:
                log_warn(f"Plot {plot_num:>3}: Executed but no figure file produced — {plot_name}")
                failed.append({
                    'number': plot_num,
                    'name': plot_name,
                    'error': 'No figure file produced after execution.',
                })

        except Exception as e:
            tb = traceback.format_exc()
            log_error(f"Plot {plot_num:>3}: {plot_name}")
            log_error(f"  Error: {e}")
            failed.append({
                'number': plot_num,
                'name': plot_name,
                'error': str(e),
                'traceback': tb,
            })

            # Clean up even on failure
            try:
                exec('import matplotlib.pyplot as _plt; _plt.close("all")', namespace)
            except Exception:
                pass

    return successful, failed


# ---------------------------------------------------------------------------
# Step 5 — Generate data.json and failed_plots.json
# ---------------------------------------------------------------------------

def generate_data_json(
    successful: list[dict],
    phase_headers: list[tuple[int, int]],
) -> None:
    """
    Write data.json containing metadata for all successfully executed plots.
    """
    data = []
    for marker in successful:
        plot_num = marker['number']
        difficulty = determine_difficulty(marker['char_pos'], phase_headers)

        entry = {
            "id": plot_num,
            "name": marker['name'],
            "difficulty": difficulty,
            "tags": [],
            "image": f"figures/{plot_num}.png",
            "code_file": f"code_snippets/{plot_num}.txt",
        }
        data.append(entry)

    # Sort by id
    data.sort(key=lambda x: x['id'])

    path = Path("data.json")
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    log_success(f"Generated data.json with {len(data)} entries.")


def generate_failed_json(failed: list[dict]) -> None:
    """Write failed_plots.json listing failed plot numbers and errors."""
    output = []
    for item in failed:
        output.append({
            "number": item['number'],
            "name": item.get('name', ''),
            "error": item.get('error', ''),
            "traceback": item.get('traceback', ''),
        })

    path = Path("failed_plots.json")
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
    if failed:
        log_warn(f"Generated failed_plots.json with {len(failed)} entries.")
    else:
        log_info("Generated failed_plots.json (empty — all plots succeeded!).")


# ---------------------------------------------------------------------------
# Step 6 — Print summary
# ---------------------------------------------------------------------------

def print_summary(
    total: int,
    successful_count: int,
    failed: list[dict],
) -> None:
    """Print a colored summary of the splitter run."""
    log_header("SPLITTER SUMMARY")

    print(f"  {Colors.BOLD}Total plots found:{Colors.RESET}       {total}")
    print(f"  {Colors.GREEN}Successfully saved:{Colors.RESET}      {successful_count}")
    print(f"  {Colors.RED}Failed:{Colors.RESET}                   {len(failed)}")

    if failed:
        print(f"\n  {Colors.YELLOW}Failed plot numbers:{Colors.RESET}")
        for item in failed:
            print(f"    {Colors.RED}x{Colors.RESET} Plot {item['number']}: {item.get('name', '?')} -- {item.get('error', 'Unknown error')}")

    print(f"\n  {Colors.BOLD}Generated files:{Colors.RESET}")
    print(f"    {Colors.CYAN}->{Colors.RESET} figures/           ({successful_count} PNG files)")
    print(f"    {Colors.CYAN}->{Colors.RESET} code_snippets/     ({total} TXT files)")
    print(f"    {Colors.CYAN}->{Colors.RESET} data.json          (gallery metadata)")
    print(f"    {Colors.CYAN}->{Colors.RESET} failed_plots.json  (error details)")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Main entry point for the SeabornGallery splitter script."""
    log_header("SeabornGallery Splitter")

    # Step 1 — Setup
    log_info("Step 1: Setting up directories...")
    setup_directories()

    # Step 2 — Parse master file
    log_info("Step 2: Parsing src/master_plots.py...")
    master_path = Path("src") / "master_plots.py"

    try:
        content = read_master_file(master_path)
    except FileNotFoundError as e:
        print(str(e))
        return

    # 2a — Find phase headers
    phase_headers = find_phase_headers(content)
    log_info(f"Found {len(phase_headers)} phase headers.")

    # 2b — Find plot markers
    markers = find_plot_markers(content)
    log_info(f"Found {len(markers)} plot markers.")

    if not markers:
        log_error("No plot markers found! Ensure your master file uses the format: # 1 Plot Name")
        return

    # 2c/2d — names and difficulty are stored in markers already

    # 2e — Extract setup block and code blocks
    setup_block = extract_setup_block(content, markers[0]['char_pos'])
    code_blocks = extract_code_blocks(content, markers)
    log_info(f"Extracted setup block ({len(setup_block)} chars) and {len(code_blocks)} code blocks.")

    # Step 3 — Save code snippets
    log_info("Step 3: Saving code snippets...")
    save_code_snippets(code_blocks)

    # Step 4 — Execute plots
    log_info("Step 4: Executing plots and saving figures...")
    successful, failed = execute_plots(setup_block, code_blocks, markers)

    # Step 5 — Generate JSON files
    log_info("Step 5: Generating data.json and failed_plots.json...")
    generate_data_json(successful, phase_headers)
    generate_failed_json(failed)

    # Step 6 — Summary
    print_summary(
        total=len(markers),
        successful_count=len(successful),
        failed=failed,
    )


if __name__ == "__main__":
    main()
