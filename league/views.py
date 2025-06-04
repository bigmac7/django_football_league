from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Team, Match
from collections import defaultdict

def league_table(request):
    teams = Team.objects.all()
    team_stats = defaultdict(lambda: {
        'played': 0, 'wins': 0, 'draws': 0, 'losses': 0,
        'goals_for': 0, 'goals_against': 0, 'goal_difference': 0, 'points': 0
    })

    matches = Match.objects.all()

    for matchy in matches:
        home_team_stats = team_stats[matchy.home_team.name]
        away_team_stats = team_stats[matchy.away_team.name]

        # Update played matches
        home_team_stats['played'] += 1
        away_team_stats['played'] += 1

        # Update goals
        home_team_stats['goals_for'] += matchy.home_score
        home_team_stats['goals_against'] += matchy.away_score
        away_team_stats['goals_for'] += matchy.away_score
        away_team_stats['goals_against'] += matchy.home_score

        # Determine outcome and update points/wins/draws/losses
        if matchy.home_score > matchy.away_score:
            home_team_stats['wins'] += 1
            home_team_stats['points'] += 3
            away_team_stats['losses'] += 1
        elif matchy.home_score < matchy.away_score:
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
    # 1. By points (descending)
    # 2. By goal difference (descending)
    # 3. By goals for (descending)
    # 4. By team name (ascending - alphabetical tie-breaker)
    sorted_table.sort(key=lambda x: (
        x['points'],
        x['goal_difference'],
        x['goals_for'],
        x['team_name'] # Final tie-breaker, alphabetically
    ), reverse=True) # Reverse for points, GD, GF to be descending

    context = {
        'league_table': sorted_table,
    }
    return render(request, 'league_table.html', context)