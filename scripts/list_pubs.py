import os
import glob
from pybtex.database import parse_file

def render_pubs(bib_file, author_highlight=None):
    """
    Reads a bib file and prints Markdown for Quarto to render.
    """
    # 1. Check if file exists relative to the current QMD file
    if not os.path.exists(bib_file):
        print(f"**Error:** Could not find bibliography file: `{bib_file}`")
        return

    # 2. Parse the file
    try:
        bib_data = parse_file(bib_file)
    except Exception as e:
        print(f"**Error parsing bib file:** {e}")
        return
    
    # 3. Sort by year (descending)
    entries = sorted(bib_data.entries.items(), 
                     key=lambda x: x[1].fields.get('year', '0000'), 
                     reverse=True)

    # 4. Generate Markdown
    for key, entry in entries:
        year = entry.fields.get('year', 'n.d.')
        title = entry.fields.get('title', 'Untitled').replace("{", "").replace("}", "")
        # Try to get journal, then booktitle, then publisher
        venue = entry.fields.get('journal', 
                    entry.fields.get('booktitle', 
                        entry.fields.get('publisher', 'Preprint')))
        
        doi = entry.fields.get('doi', '')
        doi_str = ""
        if doi:
            # Clean up: If the bib entry already has 'https://doi.org/', remove it
            # so we can cleanly rebuild the standard link format.
            clean_doi = doi.replace("https://doi.org/", "").replace("http://dx.doi.org/", "")
            doi_str = f" [[Link](https://doi.org/{clean_doi})]"
        
        # Format Authors
        authors = []
        for person in entry.persons.get('author', []):
            name = f"{person.first_names[0]} {person.last_names[0]}"
            # Highlight logic
            if author_highlight and author_highlight in name:
                name = f"**{name}**"
            authors.append(name)
        
        author_str = ", ".join(authors)

        # Print the final Markdown Bullet
        print(f"\n1. {author_str} ({year}). **{title}.** *{venue}*.{doi_str}\n")

def get_current_page_title():
    """
    Scans the current directory for a .qmd file and extracts the 'title'.
    """
    # Find the QMD file (excluding included files)
    qmd_files = glob.glob("*.qmd")
    if not qmd_files:
        return None
    
    # Simple parser to find "title: ..." without needing extra libraries
    target_file = qmd_files[0] # Assume the main file is the first one found
    with open(target_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("title:"):
                raw_title = line.split(":", 1)[1].strip().strip('"').strip("'")
                return raw_title
    return None

def render_auto():
    """
    The Magic Function: Finds bibs, finds name, and renders.
    """
    # 1. Auto-detect Name from Page Title
    clean_name = get_current_page_title()

    # 2. Find all .bib files in the current folder
    bib_files = glob.glob("*.bib")
    
    if not bib_files:
        print("*No bibliography found in this folder.*")
        return

    # 3. Render each one
    for bib in bib_files:
        render_pubs(bib, author_highlight=clean_name)