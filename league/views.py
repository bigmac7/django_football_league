# league/views.py
from django.shortcuts import render
from .models import Team, Match
from collections import defaultdict
from django.db.models import Q # Import Q for filtering (optional but good practice)

def league_table(request):
    teams = Team.objects.all()
    team_stats = defaultdict(lambda: {
        'played': 0, 'wins': 0, 'draws': 0, 'losses': 0,
        'goals_for': 0, 'goals_against': 0, 'goal_difference': 0, 'points': 0
    })

    matches = Match.objects.all()

    for match in matches:
        home_team_stats = team_stats[match.home_team.name]
        away_team_stats = team_stats[match.away_team.name]

        # Update played matches
        home_team_stats['played'] += 1
        away_team_stats['played'] += 1

        # Update goals
        home_team_stats['goals_for'] += match.home_score
        home_team_stats['goals_against'] += match.away_score
        away_team_stats['goals_for'] += match.away_score
        away_team_stats['goals_against'] += match.home_score

        # Determine outcome and update points/wins/draws/losses
        if match.home_score > match.away_score:
            home_team_stats['wins'] += 1
            home_team_stats['points'] += 3
            away_team_stats['losses'] += 1
        elif match.home_score < match.away_score:
            away_team_stats['wins'] += 1
            away_team_stats['points'] += 3
            home_team_stats['losses'] += 1
        else:
            home_team_stats['draws'] += 1
            away_team_stats['draws'] += 1
            home_team_stats['points'] += 1
            away_team_stats['points'] += 1

    # Calculate goal difference after all matches processed
    for team_name, stats in team_stats.items():
        stats['goal_difference'] = stats['goals_for'] - stats['goals_against']

    # Convert defaultdict to a list of dicts for sorting
    sorted_table = []
    for team_name, stats in team_stats.items():
        sorted_table.append({
            'team_name': team_name,
            **stats
        })

    # Sort the table:
    sorted_table.sort(key=lambda x: (
        x['points'],
        x['goal_difference'],
        x['goals_for'],
        x['team_name']
    ), reverse=True)

    # --- New: Get recent fixtures ---
    # Fetch all matches, ordered by match_date (most recent first) and slice to get the first 5
    recent_fixtures = Match.objects.all().order_by('-match_date')[:5]

    context = {
        'league_table': sorted_table,
        'recent_fixtures': recent_fixtures, # Add to context
    }
    return render(request, 'league_table.html', context)