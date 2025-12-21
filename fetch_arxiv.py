#!/usr/bin/env python3
"""
Fetch recent ArXiv papers from AI/ML categories and save to JSON.
"""

import arxiv
import json
from datetime import datetime, timedelta
from pathlib import Path


# Categories to monitor
CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CY"]

# Fetch papers from last 7 days (for testing; change to 1 for production)
def fetch_recent_papers(days=7):
    """Fetch papers from the last N days across specified categories."""
    papers = []
    client = arxiv.Client()

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    print(f"Fetching papers from {start_date.date()} to {end_date.date()}...")

    for category in CATEGORIES:
        print(f"Searching category: {category}")

        # Search query for this category, sorted by submission date
        search = arxiv.Search(
            query=f"cat:{category}",
            max_results=200,  # Get up to 200 papers per category
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )

        # Fetch results using Client (fixes deprecation warning)
        for result in client.results(search):
            # Only include papers published in the specified date range
            if result.published.replace(tzinfo=None) >= start_date:
                paper = {
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "abstract": result.summary.replace("\n", " "),
                    "link": result.entry_id,
                    "published": result.published.isoformat(),
                    "categories": result.categories,
                    "primary_category": result.primary_category
                }
                papers.append(paper)
            else:
                # Papers are sorted by date, so we can break once we hit older ones
                break

    print(f"Found {len(papers)} papers total")
    return papers


def save_to_json(papers, days=7):
    """Save papers to JSON file with timestamp."""
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Generate filename with today's date
    filename = f"data/arxiv-{datetime.now().strftime('%Y-%m-%d')}.json"

    # Also save to latest.json for easy access
    latest_file = "data/latest.json"

    output = {
        "fetched_at": datetime.now().isoformat(),
        "date_range": {
            "start": (datetime.now() - timedelta(days=days)).isoformat(),
            "end": datetime.now().isoformat()
        },
        "count": len(papers),
        "papers": papers
    }

    # Save dated version
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Saved to {filename}")

    # Save latest version
    with open(latest_file, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Saved to {latest_file}")


if __name__ == "__main__":
    # For testing: fetch last 7 days of papers
    # For production (GitHub Actions): change to days=1
    DAYS = 7
    papers = fetch_recent_papers(days=DAYS)
    save_to_json(papers, days=DAYS)
    print("Done!")
